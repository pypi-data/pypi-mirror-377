import math
import os
import warnings
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss

from transformers import(
    BertPreTrainedModel,
    BertModel,
    BertConfig,
    RobertaPreTrainedModel,
    RobertaModel,
    XLMRobertaPreTrainedModel,
    XLMRobertaModel,
    XLMRobertaXLPreTrainedModel,
    XLMRobertaXLModel,
    DebertaPreTrainedModel,
    DebertaModel,
    DebertaV2PreTrainedModel,
    DebertaV2Model,
    ElectraPreTrainedModel,
    ElectraModel,
    AlbertPreTrainedModel,
    AlbertModel
)
from transformers.utils import (
    ModelOutput,
    logging,
    replace_return_docstrings,
)
# This is internal and not recommended for production use
from transformers.utils.doc import add_start_docstrings, add_start_docstrings_to_model_forward, add_code_sample_docstrings
from transformers.modeling_outputs import TokenClassifierOutput
# from transformers.models.bert.modeling_bert import (
#     BERT_START_DOCSTRING,
#     BERT_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as BERT_CONFIG_FOR_DOC,
#     _TOKEN_CLASS_EXPECTED_OUTPUT as BERT_TOKEN_CLASS_EXPECTED_OUTPUT,
#     _TOKEN_CLASS_EXPECTED_LOSS as BERT_TOKEN_CLASS_EXPECTED_LOSS,
#     _CHECKPOINT_FOR_TOKEN_CLASSIFICATION as BERT_CHECKPOINT_FOR_TOKEN_CLASSIFICATION
# )
# from transformers.models.roberta.modeling_roberta import (
#     ROBERTA_START_DOCSTRING,
#     ROBERTA_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as ROBERTA_CONFIG_FOR_DOC
# )
# from transformers.models.xlm_roberta.modeling_xlm_roberta import (
#     XLM_ROBERTA_START_DOCSTRING,
#     XLM_ROBERTA_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as XLM_ROBERTA_CONFIG_FOR_DOC
# )
# from transformers.models.xlm_roberta_xl.modeling_xlm_roberta_xl import (
#     XLM_ROBERTA_XL_START_DOCSTRING,
#     XLM_ROBERTA_XL_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as XLM_ROBERTA_XL_CONFIG_FOR_DOC,
#     _CHECKPOINT_FOR_DOC as XLM_ROBERTA_XL_CHECKPOINT_FOR_DOC
# )
# from transformers.models.deberta.modeling_deberta import (
#     DEBERTA_START_DOCSTRING,
#     DEBERTA_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as DEBERTA_CONFIG_FOR_DOC,
#     _CHECKPOINT_FOR_DOC as DEBERTA_CHECKPOINT_FOR_DOC
# )
# from transformers.models.deberta_v2.modeling_deberta_v2 import (
#     DEBERTA_START_DOCSTRING as DEBERTAV2_START_DOCSTRING,
#     DEBERTA_INPUTS_DOCSTRING as DEBERTAV2_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as DEBERTAV2_CONFIG_FOR_DOC,
#     _CHECKPOINT_FOR_DOC as DEBERTAV2_CHECKPOINT_FOR_DOC
# )
# from transformers.models.electra.modeling_electra import (
#     ELECTRA_START_DOCSTRING,
#     ELECTRA_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as ELECTRA_CONFIG_FOR_DOC
# )
# from transformers.models.albert.modeling_albert import (
#     ALBERT_START_DOCSTRING,
#     ALBERT_INPUTS_DOCSTRING,
#     _CONFIG_FOR_DOC as ALBERT_CONFIG_FOR_DOC,
#     _CHECKPOINT_FOR_DOC as ALBERT_CHECKPOINT_FOR_DOC
# )

from transformers_crf.crf import CRF, CRFwithConstraints
from transformers_crf.transformer_embedder import TransformerEmbedder
from transformers_crf.util import get_tokens_mask

@dataclass
class TokenPredsOutput(TokenClassifierOutput):
    original_order: Optional[torch.Tensor] = None
    predicts: Optional[torch.Tensor] = None

class EmbedderCRFModule(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.num_labels = config.num_labels
        self.constrain_crf = config.constrain_crf

        self.embedder = TransformerEmbedder(config, sub_token_mode='first')

        classifier_dropout = (
            config.classifier_dropout if config.classifier_dropout is not None else config.hidden_dropout_prob
        )
        self.dropout = nn.Dropout(classifier_dropout)

        self.classifier = nn.Linear(config.hidden_size, config.num_labels)

        if self.constrain_crf:
            id2label_list = [v for k, v in config.id2label.items()]
            self.crf = CRFwithConstraints(
                id2label_list, batch_first=True, add_constraint=True
            )
        else:
            self.crf = CRF(num_tags=config.num_labels, batch_first=True)

    def forward(
        self,
        sequence_output: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        reorder: bool = False,
        outputs: Optional[Union[ModelOutput, torch.Tensor]] = None,
        return_dict: Optional[bool] = None
    ) -> Union[Tuple[torch.Tensor], TokenPredsOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        embed_sequence_output = self.embedder(
            sequence_output,
            #has_special_tokens=has_special_tokens,
            offsets=offsets,
            mask=mask
        )

        embed_sequence_output = self.dropout(embed_sequence_output)
        logits = self.classifier(embed_sequence_output)

        crf_mask = get_tokens_mask(mask, attention_mask, logits.size(1))
        
        loss = None
        if labels is not None:
            loss = -self.crf(logits, labels * crf_mask, reduction='mean', mask=crf_mask)
        
        predicts = self.crf.decode(logits, mask=crf_mask).squeeze(0)

        if original_order is None:
            original_order = torch.arange(sequence_output.size(0), device=sequence_output.device)
        
        if reorder:
            sort_index = torch.argsort(original_order)
            predicts = predicts[sort_index]  
            logits = logits[sort_index]

            if not return_dict:
                for i, output in enumerate(outputs[2:]):
                    if output is not None:
                        outputs[i+2] = output[sort_index]
            else:        
                if outputs.attentions is not None:
                    outputs.attentions = outputs.attentions[sort_index]
                if outputs.attentions is not None:
                    outputs.attentions = outputs.attentions[sort_index]

        if not return_dict:
            output = (logits,) + outputs[2:]
            output = ((loss,) + output) if loss is not None else output
            output = ((original_order,) + output) if loss is not None else output
            output = ((predicts,) + output) if predicts is not None else output
            return output
        
        return TokenPredsOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            original_order=original_order,
            predicts=predicts
        )
        #return logits, loss, predicts


@add_start_docstrings(
    """
    Bert Model transformer with a sequence CRF classification head on top
    """,
    BertModel.__doc__,
)
class BertForEmbedderCRFTokenClassification(BertPreTrainedModel):

    _no_split_modules = ["BertModel", "BertEmbeddings", "BertSelfAttention"]

    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.use_crf = True
        config.use_crf = True

        self.bert = BertModel(config, add_pooling_layer=False)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(BertModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint=BERT_CHECKPOINT_FOR_TOKEN_CLASSIFICATION,
    #     output_type=TokenClassifierOutput,
    #     config_class=BertConfig.__doc__,
    #     expected_output=BERT_TOKEN_CLASS_EXPECTED_OUTPUT,
    #     expected_loss=BERT_TOKEN_CLASS_EXPECTED_LOSS,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenPredsOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """

        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        
        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        
        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    Roberta Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for
    Named-Entity-Recognition (NER) tasks.
    """,
    RobertaModel.__doc__,
)
class RobertaForEmbedderCRFTokenClassification(RobertaPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.use_crf = True
        config.use_crf = True

        self.roberta = RobertaModel(config, add_pooling_layer=False)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(RobertaModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint="Jean-Baptiste/roberta-large-ner-english",
    #     output_type=TokenClassifierOutput,
    #     config_class=ROBERTA_CONFIG_FOR_DOC,
    #     expected_output="['O', 'ORG', 'ORG', 'O', 'O', 'O', 'O', 'O', 'LOC', 'O', 'LOC', 'LOC']",
    #     expected_loss=0.01,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    XLM-RoBERTa Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g.
    for Named-Entity-Recognition (NER) tasks.
    """,
    XLMRobertaModel.__doc__,
)
# Copied from transformers.models.roberta.modeling_roberta.RobertaForTokenClassification with Roberta->XLMRoberta, ROBERTA->XLM_ROBERTA
class XLMRobertaForEmbedderCRFTokenClassification(XLMRobertaPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.roberta = XLMRobertaModel(config, add_pooling_layer=False)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(XLMRobertaModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint="Jean-Baptiste/roberta-large-ner-english",
    #     output_type=TokenClassifierOutput,
    #     config_class=XLM_ROBERTA_CONFIG_FOR_DOC,
    #     expected_output="['O', 'ORG', 'ORG', 'O', 'O', 'O', 'O', 'O', 'LOC', 'O', 'LOC', 'LOC']",
    #     expected_loss=0.01,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    XLM-Roberta-xlarge Model with a token classification head on top (a linear layer on top of the hidden-states
    output) e.g. for Named-Entity-Recognition (NER) tasks.
    """,
    XLMRobertaXLModel.__doc__,
)
class XLMRobertaXLForEmbedderCRFTokenClassification(XLMRobertaXLPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.roberta = XLMRobertaXLModel(config, add_pooling_layer=False)
        self.embedder_crf = EmbedderCRFModule(config)

        self.init_weights()

    @add_start_docstrings_to_model_forward(XLMRobertaXLModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint=XLM_ROBERTA_XL_CHECKPOINT_FOR_DOC,
    #     output_type=TokenClassifierOutput,
    #     config_class=XLM_ROBERTA_XL_CONFIG_FOR_DOC,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    DeBERTa Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for
    Named-Entity-Recognition (NER) tasks.
    """,
    DebertaModel.__doc__,
)
class DebertaForEmbedderCRFTokenClassification(DebertaPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.deberta = DebertaModel(config)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(DebertaModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint=DEBERTA_CHECKPOINT_FOR_DOC,
    #     output_type=TokenClassifierOutput,
    #     config_class=DEBERTA_CONFIG_FOR_DOC,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.deberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    DeBERTa Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for
    Named-Entity-Recognition (NER) tasks.
    """,
    DebertaV2Model.__doc__,
)
# Copied from transformers.models.deberta.modeling_deberta.DebertaForTokenClassification with Deberta->DebertaV2
class DebertaV2ForEmbedderCRFTokenClassification(DebertaV2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.deberta = DebertaV2Model(config)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(DebertaV2Model.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint=DEBERTAV2_CHECKPOINT_FOR_DOC,
    #     output_type=TokenClassifierOutput,
    #     config_class=DEBERTAV2_CONFIG_FOR_DOC,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.deberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    Electra model with a token classification head on top.

    Both the discriminator and generator may be loaded into this model.
    """,
    ElectraModel.__doc__,
)
class ElectraForEmbedderCRFTokenClassification(ElectraPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.electra = ElectraModel(config)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(ElectraModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint="bhadresh-savani/electra-base-discriminator-finetuned-conll03-english",
    #     output_type=TokenClassifierOutput,
    #     config_class=ELECTRA_CONFIG_FOR_DOC,
    #     expected_output="['B-LOC', 'B-ORG', 'O', 'O', 'O', 'O', 'O', 'B-LOC', 'O', 'B-LOC', 'I-LOC']",
    #     expected_loss=0.11,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.electra(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )
    
@add_start_docstrings(
    """
    Albert Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for
    Named-Entity-Recognition (NER) tasks.
    """,
    AlbertModel.__doc__,
)
class AlbertForEmbedderCRFTokenClassification(AlbertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.albert = AlbertModel(config, add_pooling_layer=False)
        self.embedder_crf = EmbedderCRFModule(config)

        # Initialize weights and apply final processing
        self.post_init()

    @add_start_docstrings_to_model_forward(AlbertModel.forward.__doc__.format("batch_size, sequence_length"))
    # @add_code_sample_docstrings(
    #     checkpoint=ALBERT_CHECKPOINT_FOR_DOC,
    #     output_type=TokenClassifierOutput,
    #     config_class=ALBERT_CONFIG_FOR_DOC,
    # )
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        offsets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        original_order: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        reorder: bool = False
    ) -> Union[Tuple[torch.Tensor], TokenClassifierOutput]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the token classification loss. Indices should be in `[0, ..., config.num_labels - 1]`.
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.albert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0] if not return_dict else outputs.last_hidden_state
        
        return self.embedder_crf(
            sequence_output=sequence_output,
            attention_mask=attention_mask,
            offsets=offsets,
            mask=mask,
            labels=labels,
            original_order=original_order,
            reorder=reorder,
            outputs=outputs,
            return_dict=return_dict
        )


from transformers import (
    BertConfig,
    RobertaConfig,
    XLMRobertaConfig,
    XLMRobertaXLConfig,
    DebertaConfig,
    DebertaV2Config,
    ElectraConfig,
    AlbertConfig
)
from collections import OrderedDict
from transformers.models.auto.configuration_auto import CONFIG_MAPPING_NAMES
from transformers.models.auto.auto_factory import _BaseAutoModelClass, _LazyAutoMapping, auto_class_update

MODEL_FOR_CRF_TOKEN_CLASSIFICATION_MAPPING_NAMES = OrderedDict(
    [
        # Model for Token Classification mapping
        #("bert", "BertForEmbedderCRFTokenClassification"),
    ]
)

MODEL_FOR_CRF_TOKEN_CLASSIFICATION_MAPPING = _LazyAutoMapping(
    CONFIG_MAPPING_NAMES, MODEL_FOR_CRF_TOKEN_CLASSIFICATION_MAPPING_NAMES
)

class AutoModelForEmbedderCRFTokenClassification(_BaseAutoModelClass):
    _model_mapping = MODEL_FOR_CRF_TOKEN_CLASSIFICATION_MAPPING


AutoModelForEmbedderCRFTokenClassification = auto_class_update(AutoModelForEmbedderCRFTokenClassification, head_doc="token crf classification")
AutoModelForEmbedderCRFTokenClassification.register(BertConfig, BertForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(RobertaConfig, RobertaForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(XLMRobertaConfig, XLMRobertaForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(XLMRobertaXLConfig, XLMRobertaXLForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(DebertaConfig, DebertaForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(DebertaV2Config, DebertaV2ForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(ElectraConfig, ElectraForEmbedderCRFTokenClassification)
AutoModelForEmbedderCRFTokenClassification.register(AlbertConfig, AlbertForEmbedderCRFTokenClassification)
