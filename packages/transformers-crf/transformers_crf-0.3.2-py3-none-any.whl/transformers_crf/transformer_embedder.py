# Copyright (c) Alibaba, Inc. and its affiliates.
# Copyright (c) AI2 AllenNLP. Licensed under the Apache License, Version 2.0.
# from adaseq

from typing import Any, Dict, Optional, Tuple
import transformers
import torch
from torch import nn
from transformers import AutoConfig, AutoModel, XLNetConfig

import transformers_crf.util as util

# Code partially borrowed from https://github.com/allenai/allennlp/blob/HEAD/
# allennlp/modules/token_embedders/pretrained_transformer_embedder.py
class TransformerEmbedder(nn.Module):
    """
    Uses a pretrained model from `transformers` as a `Embedder`.

    # Parameters

    model_name_or_path : `str`
        The name of the `transformers` model to use. Should be the same as the corresponding
        `PretrainedTransformerIndexer`.
    drop_special_tokens:  `bool` (default = `True`)
        if `True`, drop the hidden states of special tokens (currently [CLS], [SEP]).
    sub_module: `str`, optional (default = `None`)
        The name of a submodule of the transformer to be used as the embedder. Some transformers naturally act
        as embedders such as BERT. However, other models consist of encoder and decoder, in which case we just
        want to use the encoder.
    train_parameters: `bool`, optional (default = `True`)
        If this is `True`, the transformer weights get updated during training. If this is `False`, the
        transformer weights are not updated during training.
    eval_mode: `bool`, optional (default = `False`)
        If this is `True`, the model is always set to evaluation mode (e.g., the dropout is disabled and the
        batch normalization layer statistics are not updated). If this is `False`, such dropout and batch
        normalization layers are only set to evaluation mode when when the model is evaluating on development
        or test data.
    load_weights: `bool`, optional (default = `True`)
        Whether to load the pretrained weights. If you're loading your model/predictor from an AllenNLP archive
        it usually makes sense to set this to `False` (via the `overrides` parameter)
        to avoid unnecessarily caching and loading the original pretrained weights,
        since the archive will already contain all of the weights needed.
    scalar_mix: `Dict[str, Any]`, optional (default = `None`)
        When `None` (the default), only the final layer of the pretrained transformer is taken
        for the embeddings.
        If pass a kwargs dict, a scalar mix of all of the layers is used.
    gradient_checkpointing: `bool`, optional (default = `None`)
        Enable or disable gradient checkpointing.
    transformer_kwargs: `Dict[str, Any]`, optional (default = `None`)
        Dictionary with additional arguments for `get_transformer`.
    sub_token_mode: `str`, (default= `first`)
        If `sub_token_mode` is set to `first`, return first sub-token representation as word-level representation.
        If `sub_token_mode` is set to `last`, return last sub-token representation as word-level representation.
        If `sub_token_mode` is set to `avg`, return average of all the sub-tokens
        representation as word-level representation.
        If `sub_token_mode` is not specified it defaults to `avg`
        If invalid `sub_token_mode` is provided, throw `ConfigurationError`
    """

    def __init__(
        self,
        config,
        *,
        drop_special_tokens: bool = True,
        #scalar_mix: Optional[Dict[str, Any]] = None,
        sub_token_mode: str = 'first',
    ) -> None:
        super().__init__()
        self.drop_special_tokens = drop_special_tokens
        self.sub_token_mode = sub_token_mode

        self.config = config

        # I'm not sure if this works for all models; open an issue on github if you find a case
        # where it doesn't work.
        self.output_dim = self.config.hidden_size

        self._scalar_mix = None#: Optional[ScalarMix] = None
        #if scalar_mix:
        #    self._scalar_mix = ScalarMix(self.config.num_hidden_layers, **scalar_mix)
        #    self.config.output_hidden_states = True

        if isinstance(self.config, XLNetConfig):
            self._number_of_token_type_embeddings = 3  # XLNet has 3 type ids
        elif hasattr(self.config, 'type_vocab_size'):
            self._number_of_token_type_embeddings = self.config.type_vocab_size
        else:
            self._number_of_token_type_embeddings = 0

    def get_output_dim(self):  # noqa: D102
        return self.output_dim

    def forward(
        self,
        last_hidden_state: torch.Tensor,
        offsets: Optional[torch.LongTensor] = None,
        #has_special_tokens: Optional[torch.BoolTensor] = None,
        mask: Optional[torch.BoolTensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        """
        input_ids: `torch.LongTensor`
            Shape: [batch_size, num_orig_tokens or num_wordpieces].
        attention_mask: `torch.BoolTensor`
            Shape: [batch_size, num_orig_tokens or num_wordpieces].
        token_type_ids: `Optional[torch.LongTensor]`
            Shape: [batch_size, num_orig_tokens or num_wordpieces].
        offsets: `torch.LongTensor`
            Shape: [batch_size, num_orig_tokens, 2].
            Maps indices for the original tokens, i.e. those given as input to the indexer,
            to a span in input_ids. `input_ids[i][offsets[i][j][0]:offsets[i][j][1] + 1]`
            corresponds to the original j-th token from the i-th batch.
        mask: `torch.BoolTensor`
            Shape: [batch_size, num_orig_tokens].

        # Returns

        `torch.Tensor`
            Shape: `[batch_size, num_wordpieces or num_orig_tokens, embedding_size]`.
        """
        # first encode sub-token level representations
        #encoded = self.encode(input_ids, attention_mask, token_type_ids)  # type: ignore
        encoded = last_hidden_state
        if offsets is not None:
            # then reconstruct token-level ones by offsets
            encoded = self.reconstruct(encoded, offsets)

        #if has_special_tokens is not None:
        #always habe special tokens
        if self.drop_special_tokens:# and has_special_tokens.bool()[0]:
            encoded = encoded[:, 1:-1]  # So far, we only consider [CLS] and [SEP]
        return encoded

    def reconstruct(self, embeddings: torch.Tensor, offsets: torch.LongTensor) -> torch.Tensor:
        """
        # Parameters

        input_ids: `torch.LongTensor`
            Shape: [batch_size, num_wordpieces].
        offsets: `torch.LongTensor`
            Shape: [batch_size, num_orig_tokens, 2].
            Maps indices for the original tokens, i.e. those given as input to the indexer,
            to a span in input_ids. `input_ids[i][offsets[i][j][0]:offsets[i][j][1] + 1]`
            corresponds to the original j-th token from the i-th batch.

        # Returns

        `torch.Tensor`
            Shape: [batch_size, num_orig_tokens, embedding_size].
        """

        # If "sub_token_mode" is set to "first", return the first sub-token embedding
        if self.sub_token_mode == 'first':
            # Select first sub-token embeddings from span embeddings
            # Shape: (batch_size, num_orig_tokens, embedding_size)
            orig_embeddings = util.batched_index_select(embeddings, offsets[..., 0])

        # If "sub_token_mode" is set to "last", return the last sub-token embedding
        elif self.sub_token_mode == 'last':
            # Select last sub-token embeddings from span embeddings
            # Shape: (batch_size, num_orig_tokens, embedding_size)
            orig_embeddings = util.batched_index_select(embeddings, offsets[..., 1])

        # If "sub_token_mode" is set to "avg", return the average of embeddings of all sub-tokens of a word
        elif self.sub_token_mode == 'avg':
            # span_embeddings: (batch_size, num_orig_tokens, max_span_length, embedding_size)
            # span_mask: (batch_size, num_orig_tokens, max_span_length)
            span_embeddings, span_mask = util.batched_span_select(embeddings.contiguous(), offsets)

            span_mask = span_mask.unsqueeze(-1)

            # Shape: (batch_size, num_orig_tokens, max_span_length, embedding_size)
            span_embeddings *= span_mask  # zero out paddings

            # Sum over embeddings of all sub-tokens of a word
            # Shape: (batch_size, num_orig_tokens, embedding_size)
            span_embeddings_sum = span_embeddings.sum(2)

            # Shape (batch_size, num_orig_tokens)
            span_embeddings_len = span_mask.sum(2)

            # Find the average of sub-tokens embeddings by dividing `span_embedding_sum` by `span_embedding_len`
            # Shape: (batch_size, num_orig_tokens, embedding_size)
            orig_embeddings = span_embeddings_sum / torch.clamp_min(span_embeddings_len, 1)

            # All the places where the span length is zero, write in zeros.
            orig_embeddings[(span_embeddings_len == 0).expand(orig_embeddings.shape)] = 0

        # If invalid "sub_token_mode" is provided, throw error
        else:
            raise ValueError(f"Do not recognise 'sub_token_mode' {self.sub_token_mode}")

        return orig_embeddings