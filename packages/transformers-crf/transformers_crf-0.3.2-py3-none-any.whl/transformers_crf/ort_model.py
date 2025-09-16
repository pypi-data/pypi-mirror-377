########
# TODO: https://huggingface.co/docs/optimum/exporters/onnx/usage_guides/contribute
# vs https://github.com/huggingface/optimum/blob/8bdc166fcbcbb24c3dd97fd8b98dd123af282f00/optimum/exporters/onnx/model_configs.py#L69
# vs https://github.com/huggingface/optimum/blob/8bdc166fcbcbb24c3dd97fd8b98dd123af282f00/optimum/onnxruntime/modeling_ort.py#L1326
########

from typing import Optional, Union, Tuple, Dict, List, Any
import numpy as np
import torch
import random
from collections import OrderedDict
from optimum.onnxruntime import ORTModel

from optimum.onnxruntime.modeling_ort import (
    ONNX_MODEL_START_DOCSTRING,
    add_start_docstrings,
    add_start_docstrings_to_model_forward,
    ONNX_TEXT_INPUTS_DOCSTRING,
    TOKEN_CLASSIFICATION_EXAMPLE,
    _TOKENIZER_FOR_DOC
)
from optimum.exporters.onnx.config import OnnxConfig
from optimum.exporters.onnx.model_configs import DummyTextInputGenerator, NormalizedTextConfig, DEFAULT_DUMMY_SHAPES

from transformers_crf.bert_crf import AutoModelForEmbedderCRFTokenClassification, TokenPredsOutput

CRF_DEFAULT_DUMMY_SHAPES = DEFAULT_DUMMY_SHAPES.copy()

CRF_DEFAULT_DUMMY_SHAPES["batch_size"] = 8#32
CRF_DEFAULT_DUMMY_SHAPES["sequence_length"] = 512
CRF_DEFAULT_DUMMY_SHAPES["orig_tokens_length"] = 510

class CRFDummyTextInputGenerator(DummyTextInputGenerator):
    """
    Generates dummy encoder text inputs.
    """

    SUPPORTED_INPUT_NAMES = (
        "input_ids",
        "attention_mask",
        "offsets",
        "mask",
        "token_type_ids",
    )

    def __init__(
        self,
        task: str,
        normalized_config: NormalizedTextConfig,
        batch_size: int = CRF_DEFAULT_DUMMY_SHAPES["batch_size"],
        sequence_length: int = CRF_DEFAULT_DUMMY_SHAPES["sequence_length"],
        num_choices: int = CRF_DEFAULT_DUMMY_SHAPES["num_choices"],
        orig_tokens_length: int = CRF_DEFAULT_DUMMY_SHAPES["orig_tokens_length"],
        random_batch_size_range: Optional[Tuple[int, int]] = None,
        random_sequence_length_range: Optional[Tuple[int, int]] = None,
        random_num_choices_range: Optional[Tuple[int, int]] = None,
        random_orig_tokens_length_range: Optional[Tuple[int, int]] = None,
        **kwargs,
    ):
        super().__init__(
            task,
            normalized_config,
            batch_size,
            sequence_length,
            num_choices,
            random_batch_size_range,
            random_sequence_length_range,
            random_num_choices_range,
        )
        if random_orig_tokens_length_range:
            low, high = random_orig_tokens_length_range
            self.orig_tokens_length = random.randint(low, high)
        else:
            self.orig_tokens_length = orig_tokens_length
        self.orig_tokens_length = min(self.orig_tokens_length, self.sequence_length-2)

        self.random_token_lengths = np.random.randint(1, self.orig_tokens_length+1, size=self.batch_size)
        self.random_token_lengths.sort()
        self.random_token_lengths = list(self.random_token_lengths[::-1])
        self.random_token_lengths[0] = self.orig_tokens_length
    
    @staticmethod
    def random_mask_tensor(shape: List[int], token_lengths: List[int], framework: str = "pt"):
        """
        Generates a tensor of random integers in the [min_value, max_value) range.

        Args:
            shape (`List[int]`):
                The shape of the random tensor.
            max_value (`int`):
                The maximum value allowed.
            min_value (`int`, *optional*, defaults to 0):
                The minimum value allowed.
            framework (`str`, *optional*, defaults to `"pt"`):
                The requested framework.

        Returns:
            A random tensor in the requested framework.
        """
        data = np.ones(shape, dtype=np.bool)
        for i in range(1, shape[0]):
            data[i][token_lengths[i]+2:] = False
        if framework == "pt":
            return torch.tensor(data, dtype=torch.int64)
        elif framework == "tf":
            return tf.convert_to_tensor(data, dtype=tf.int64)
        else:
            return np.cast(data, dtype=np.int64)
        
    @staticmethod
    def random_offsets_tensor(shape: List[int], token_lengths: List[int], sequence_length: int, framework: str = "pt"):
        """
        Generates a tensor of random integers in the [min_value, max_value) range.

        Args:
            shape (`List[int]`):
                The shape of the random tensor.
            max_value (`int`):
                The maximum value allowed.
            min_value (`int`, *optional*, defaults to 0):
                The minimum value allowed.
            framework (`str`, *optional*, defaults to `"pt"`):
                The requested framework.

        Returns:
            A random tensor in the requested framework.
        """
        token_max_length = shape[1]
        #token_length = token_max_length
        data = np.asarray([[[0,0]]*shape[1]]*shape[0])
        #data[-1] = [sequence_length-1, sequence_length-1]

        
        for i in range(0, shape[0]):
            token_length = token_lengths[i]+2
            join_index = np.random.randint(1, token_length-1)
            i_acc = 0
            for j in range(len(data[i])):
                if j == join_index:
                    data[i][j][0] = i_acc
                    data[i][j][1] = sequence_length-(token_length-i_acc)
                    i_acc = sequence_length-(token_length-i_acc)+1
                else:
                    data[i][j][0] = i_acc
                    data[i][j][1] = i_acc
                    i_acc += 1
                if j == token_length-1:
                    break

        if framework == "pt":
            return torch.tensor(data, dtype=torch.int64)
        elif framework == "tf":
            return tf.convert_to_tensor(data, dtype=tf.int64)
        else:
            return np.cast(data, dtype=np.int64)

    def generate(self, input_name: str, framework: str = "pt"):
        min_value = 0
        max_value = 2 if input_name != "input_ids" else self.vocab_size
        shape = [self.batch_size, self.sequence_length]
        if self.task == "multiple-choice":
            shape = [self.batch_size, self.num_choices, self.sequence_length]
        elif self.task == "crf":
            shape_crf = [self.batch_size, self.orig_tokens_length+2]
            if input_name == "offsets":
                shape = shape_crf
                return self.random_offsets_tensor(shape, self.random_token_lengths, self.sequence_length, framework=framework)
            elif input_name == "mask":
                shape = shape_crf
                return self.random_mask_tensor(shape, self.random_token_lengths, framework=framework)
        return self.random_int_tensor(shape, max_value, min_value=min_value, framework=framework)

# This class is actually in optimum/exporters/onnx/config.py
class CRFTextEncoderOnnxConfig(OnnxConfig):
    # Describes how to generate the dummy inputs.
    DUMMY_INPUT_GENERATOR_CLASSES = (CRFDummyTextInputGenerator,)

class BertCRFOnnxConfig(CRFTextEncoderOnnxConfig):
    # Specifies how to normalize the BertConfig, this is needed to access common attributes
    # during dummy input generation.
    NORMALIZED_CONFIG_CLASS = NormalizedTextConfig
    # Sets the absolute tolerance to when validating the exported ONNX model against the
    # reference model.
    ATOL_FOR_VALIDATION = 1e-4
    
    def __init__(self, *args, **kwargs):
        self._TASK_TO_COMMON_OUTPUTS["crf"] = OrderedDict({
                'logits': {0: 'batch_size', 1: 'orig_tokens_length'},
                'predicts': {0: 'batch_size', 1: 'orig_tokens_length'}
            })
        super().__init__(*args, **kwargs)

    @property
    def inputs(self) -> Dict[str, Dict[int, str]]:
        if self.task == "multiple-choice":
            dynamic_axis = {0: "batch_size", 1: "num_choices", 2: "sequence_length"}
        elif self.task == "crf":
            return {
                'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
                'offsets': {0: 'batch_size', 1: 'orig_tokens_special_length'},
                'mask': {0: 'batch_size', 1: 'orig_tokens_special_length'},
            }
        else:
            dynamic_axis = {0: "batch_size", 1: "sequence_length"}
        return {
            "input_ids": dynamic_axis,
            "attention_mask": dynamic_axis,
            "token_type_ids": dynamic_axis,
        }

@add_start_docstrings(
    """
    Onnx Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g.
    for Named-Entity-Recognition (NER) tasks.
    """,
    ONNX_MODEL_START_DOCSTRING,
)
class ORTModelForEmbedderCRFTokenClassification(ORTModel):
    """
    Token Classification model for ONNX.
    """

    auto_model_class = AutoModelForEmbedderCRFTokenClassification

    @add_start_docstrings_to_model_forward(
        ONNX_TEXT_INPUTS_DOCSTRING.format("batch_size, sequence_length")
        + TOKEN_CLASSIFICATION_EXAMPLE.format(
            processor_class=_TOKENIZER_FOR_DOC,
            model_class="ORTModelForEmbedderCRFTokenClassification",
            checkpoint="optimum/bert-base-NER",
        )
    )
    def forward(
        self,
        input_ids: Optional[Union[torch.Tensor, np.ndarray]] = None,
        attention_mask: Optional[Union[torch.Tensor, np.ndarray]] = None,
        offsets: Optional[Union[torch.Tensor, np.ndarray]] = None,
        mask: Optional[Union[torch.Tensor, np.ndarray]] = None,
        token_type_ids: Optional[Union[torch.Tensor, np.ndarray]] = None,
        **kwargs,
    ):
        use_torch = isinstance(input_ids, torch.Tensor)
        self.raise_on_numpy_input_io_binding(use_torch)

        #temp
        self._ordered_input_names = ['input_ids', 'attention_mask', 'offsets', 'mask']

        if self.device.type == "cuda" and self.use_io_binding:
            io_binding, output_shapes, output_buffers = self.prepare_io_binding(
                input_ids,
                attention_mask,
                offsets,
                mask,
                #token_type_ids,
                ordered_input_names=self._ordered_input_names,
            )

            # run inference with binding & synchronize in case of multiple CUDA streams
            io_binding.synchronize_inputs()
            self.model.run_with_iobinding(io_binding)
            io_binding.synchronize_outputs()

            # converts output to namedtuple for pipelines post-processing
            return TokenPredsOutput(logits=output_buffers["logits"].view(output_shapes["logits"]),
                                    predicts=output_buffers["predicts"].view(output_shapes["predicts"]))
        else:
            if use_torch:
                input_ids = input_ids.cpu().detach().numpy()
                attention_mask = attention_mask.cpu().detach().numpy()
                offsets = offsets.cpu().detach().numpy()
                mask = mask.cpu().detach().numpy()
                if token_type_ids is not None:
                    token_type_ids = token_type_ids.cpu().detach().numpy()

            # converts pytorch inputs into numpy inputs for onnx
            onnx_inputs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "offsets": offsets,
                "mask": mask,
            }
            if token_type_ids is not None:
                onnx_inputs["token_type_ids"] = token_type_ids

            # run inference
            outputs = self.model.run(None, onnx_inputs)
            logits = outputs[self.output_names["logits"]]
            predicts = outputs[self.output_names["predicts"]]

            if use_torch:
                logits = torch.from_numpy(logits).to(self.device)
                predicts = torch.from_numpy(predicts).to(self.device)

            # converts output to namedtuple for pipelines post-processing
            return TokenPredsOutput(logits=logits, predicts=predicts)