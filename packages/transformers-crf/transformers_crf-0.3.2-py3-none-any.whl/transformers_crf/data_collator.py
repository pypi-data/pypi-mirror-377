from typing import Optional, Union, Tuple
from dataclasses import dataclass

import numpy as np

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.utils import PaddingStrategy
from transformers.data.data_collator import DataCollatorMixin

@dataclass
class DataCollatorForTokenClassificationWithCRF(DataCollatorMixin):
    """
    Data collator that will dynamically pad the inputs received, as well as the labels.

    Args:
        tokenizer ([`PreTrainedTokenizer`] or [`PreTrainedTokenizerFast`]):
            The tokenizer used for encoding the data.
        padding (`bool`, `str` or [`~utils.PaddingStrategy`], *optional*, defaults to `True`):
            Select a strategy to pad the returned sequences (according to the model's padding side and padding index)
            among:

            - `True` or `'longest'` (default): Pad to the longest sequence in the batch (or no padding if only a single
              sequence is provided).
            - `'max_length'`: Pad to a maximum length specified with the argument `max_length` or to the maximum
              acceptable input length for the model if that argument is not provided.
            - `False` or `'do_not_pad'`: No padding (i.e., can output a batch with sequences of different lengths).
        max_length (`int`, *optional*):
            Maximum length of the returned list and optionally padding length (see above).
        pad_to_multiple_of (`int`, *optional*):
            If set will pad the sequence to a multiple of the provided value.

            This is especially useful to enable the use of Tensor Cores on NVIDIA hardware with compute capability >=
            7.5 (Volta).
        label_pad_token_id (`int`, *optional*, defaults to -100):
            The id to use when padding the labels (-100 will be automatically ignore by PyTorch loss functions).
        return_tensors (`str`):
            The type of Tensor to return. Allowable values are "np", "pt" and "tf".
    """

    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    label_pad_token_id: int = -100
    offsets_pad_token = [0, 0]
    mask_pad_token: bool = False
    token_len_features_names: Tuple[int] = ('offsets', 'mask', 'original_order')
    return_tensors: str = "pt"
    sort_batch: bool = True

    def _separate_crf_features(self, features, token_len_features_names):
        token_len_features = []
        seq_len_features = []

        token_len_features = [{k: v for k, v in feature.items() if k in token_len_features_names} for feature in features]
        seq_len_features = [{k: v for k, v in feature.items() if k not in token_len_features_names} for feature in features]
        return token_len_features, seq_len_features

    def torch_call(self, features):
        import torch
        
        #sort batch descending by token length, required by the CRF class.
        token_len_features_names = list(self.token_len_features_names)
        for i, feature in enumerate(features):
            feature['original_order'] = i
        if self.sort_batch:
            features = sorted(features, key=lambda x: len(x[token_len_features_names[0]]), reverse=True)

        label_name = "label" if "label" in features[0].keys() else "labels"
        token_len_features_names.append(label_name)
        
        token_len_features, seq_len_features = self._separate_crf_features(features, token_len_features_names)
        #labels = [{label_name: feature[label_name]} for feature in features] if label_name in features[0].keys() else None
        #no_labels_features = [{k: v for k, v in feature.items() if k != label_name} for feature in features]

        batch = self.tokenizer._tokenizer.pad(
            seq_len_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )

        def to_list(tensor_or_iterable):
            if isinstance(tensor_or_iterable, torch.Tensor):
                return tensor_or_iterable.tolist()
            return list(tensor_or_iterable)
        
        batch['original_order'] = torch.tensor([feature['original_order'] for feature in token_len_features])

        #tokens_length = len(token_len_features[token_len_features_names[0]][0])
        padding_side = self.tokenizer._tokenizer.padding_side
        for feature_name, token_pad in [('offsets', self.offsets_pad_token),
                                        ('mask', self.mask_pad_token),
                                        (label_name, self.label_pad_token_id)]:
            feature_data = [feature[feature_name] for feature in token_len_features] if feature_name in token_len_features[0].keys() else None

            #padding_side = self.tokenizer.padding_side
            if feature_data is not None:
                tokens_length = len(feature_data[0])

                if padding_side == "right":
                    batch[feature_name] = [
                        to_list(data) + [token_pad] * (tokens_length - len(data)) for data in feature_data
                    ]
                else:
                    batch[feature_name] = [
                        [self.label_pad_token_id] * (tokens_length - len(data)) + to_list(data) for data in feature_data
                    ]

                if feature_name == 'mask':
                    batch[feature_name] = torch.tensor(batch[feature_name], dtype=torch.bool)
                else:
                    batch[feature_name] = torch.tensor(batch[feature_name], dtype=torch.int64)

        return batch

    def tf_call(self, features):
        import tensorflow as tf

        label_name = "label" if "label" in features[0].keys() else "labels"
        labels = [feature[label_name] for feature in features] if label_name in features[0].keys() else None
        batch = self.tokenizer.pad(
            features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            # Conversion to tensors will fail if we have labels as they are not of the same length yet.
            return_tensors="tf" if labels is None else None,
        )

        if labels is None:
            return batch

        sequence_length = tf.convert_to_tensor(batch["input_ids"]).shape[1]
        padding_side = self.tokenizer.padding_side
        if padding_side == "right":
            batch["labels"] = [
                list(label) + [self.label_pad_token_id] * (sequence_length - len(label)) for label in labels
            ]
        else:
            batch["labels"] = [
                [self.label_pad_token_id] * (sequence_length - len(label)) + list(label) for label in labels
            ]

        batch = {k: tf.convert_to_tensor(v, dtype=tf.int64) for k, v in batch.items()}
        return batch

    def numpy_call(self, features):
        label_name = "label" if "label" in features[0].keys() else "labels"
        labels = [feature[label_name] for feature in features] if label_name in features[0].keys() else None
        batch = self.tokenizer.pad(
            features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            # Conversion to tensors will fail if we have labels as they are not of the same length yet.
            return_tensors="np" if labels is None else None,
        )

        if labels is None:
            return batch

        sequence_length = np.array(batch["input_ids"]).shape[1]
        padding_side = self.tokenizer.padding_side
        if padding_side == "right":
            batch["labels"] = [
                list(label) + [self.label_pad_token_id] * (sequence_length - len(label)) for label in labels
            ]
        else:
            batch["labels"] = [
                [self.label_pad_token_id] * (sequence_length - len(label)) + list(label) for label in labels
            ]

        batch = {k: np.array(v, dtype=np.int64) for k, v in batch.items()}
        return batch