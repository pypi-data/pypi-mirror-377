from transformers import PreTrainedTokenizerFast, AutoTokenizer
from typing import List, Union, Tuple
from transformers_crf.util import encode_tokens_hf
from collections import defaultdict


class CRFTokenizer:

    def __init__(
            self,
            huggingface_tokenizer: PreTrainedTokenizerFast
    ):
        if not isinstance(huggingface_tokenizer, PreTrainedTokenizerFast):
            raise Exception(
                f"CRFTokenizer only supports PreTrainedTokenizerFast, {type(huggingface_tokenizer)} is invalid")
        self._tokenizer = huggingface_tokenizer
        self.token_len_features_names: Tuple[str, str, str] = ('offsets', 'mask', 'original_order')
        self.offsets_pad_token = [0, 0]
        self.mask_pad_token = False
        self.label_pad_token_id = -100

    @property
    def tokenizer(self) -> PreTrainedTokenizerFast:
        return self._tokenizer

    @property
    def model_max_length(self) -> int:
        return self.tokenizer.model_max_length

    @property
    def is_fast(self) -> bool:
        return self.tokenizer.is_fast

    @staticmethod
    def from_pretrained(
            pretrained_model_name_or_path: str,
            **kwargs
    ):
        if 'use_fast' in kwargs:
            if kwargs['use_fast'] is False:
                raise Exception("CRFTokenizer does not support a non fast tokenizer, use_fast has to be True")
            del kwargs['use_fast']
        huggingface_tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path, use_fast=True, **kwargs)
        return CRFTokenizer(huggingface_tokenizer)

    def __call__(
            self,
            tokens: Union[List[str], List[List[str]]],
            add_special_tokens=True,
            truncation=True,
            prepare_batch=True,
            max_length=None,
            pad_to_multiple_of=None,
            return_offsets=True,
            **kwargs
    ):
        if 'padding' in kwargs and kwargs['padding'] is True:
            raise Exception("CRFTokenizer does not support padding")
        if 'is_split_into_words' in kwargs and kwargs['is_split_into_words'] is False:
            raise Exception("CRFTokenizer has to run with is_split_into_words=True")

        # verfify input
        if isinstance(tokens, str):
            tokens = [tokens]
        elif isinstance(tokens[0], str):
            tokens = [tokens]
        if not isinstance(tokens[0], List):
            raise Exception(f"Invalid input, tokenizer has to receive a List[List[str]] but received: {tokens}")

        tokenized_inputs = defaultdict(list)

        for sent_tokens in tokens:
            data_tokenized = encode_tokens_hf(
                sent_tokens,
                self.tokenizer,
                add_special_tokens=add_special_tokens,
                truncation=truncation,
                max_length=max_length,
                return_offsets=return_offsets
            )
            for key in data_tokenized.keys():
                tokenized_inputs[key].append(data_tokenized[key])

        data = {
            "input_ids": tokenized_inputs["input_ids"],
            "attention_mask": tokenized_inputs["attention_mask"],
            "offsets": tokenized_inputs["offsets"],
            "mask": tokenized_inputs["mask"]
        }

        if prepare_batch:
            data = self.prepare_batch([
                {
                    "input_ids": data["input_ids"][i],
                    "attention_mask": data["attention_mask"][i],
                    "offsets": data["offsets"][i],
                    "mask": data["mask"][i]
                }
                for i in range(len(tokens))],
                max_length=max_length,
                pad_to_multiple_of=pad_to_multiple_of
            )

        return data

    @staticmethod
    def _separate_crf_features(features, token_len_features_names):
        token_len_features = [{k: v for k, v in feature.items() if k in token_len_features_names} for feature in
                              features]
        seq_len_features = [{k: v for k, v in feature.items() if k not in token_len_features_names} for feature in
                            features]
        return token_len_features, seq_len_features

    def prepare_batch(self,
                      features,
                      max_length=None,
                      pad_to_multiple_of=None,
                      ):
        import torch

        # sort batch descending by token length, required by the CRF class.
        token_len_features_names = list(self.token_len_features_names)
        for i, feature in enumerate(features):
            feature['original_order'] = i
        features = sorted(features, key=lambda x: len(x[token_len_features_names[0]]), reverse=True)

        label_name = 'labels' if 'labels' in features[0].keys() else 'label'
        if label_name in features[0].keys():
            token_len_features_names.append(label_name)

        token_len_features, seq_len_features = self._separate_crf_features(features, token_len_features_names)
        # labels = [{label_name: feature[label_name]} for feature in features] if label_name in features[0].keys() else None
        # no_labels_features = [{k: v for k, v in feature.items() if k != label_name} for feature in features]

        batch = self.tokenizer.pad(
            seq_len_features,
            padding=True,
            max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of,
            return_tensors="pt",
        )

        def to_list(tensor_or_iterable):
            if isinstance(tensor_or_iterable, torch.Tensor):
                return tensor_or_iterable.tolist()
            return list(tensor_or_iterable)

        batch['original_order'] = torch.tensor([feature['original_order'] for feature in token_len_features],
                                               dtype=torch.int64)
        # tokens_length = len(token_len_features[token_len_features_names[0]][0])
        padding_side = self.tokenizer.padding_side
        for feature_name, token_pad in [('offsets', self.offsets_pad_token),
                                        ('mask', self.mask_pad_token),
                                        (label_name, self.label_pad_token_id)]:
            feature_data = [feature[feature_name] for feature in token_len_features] if feature_name in \
                                                                                        token_len_features[
                                                                                            0].keys() else None

            # padding_side = self.tokenizer.padding_side
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
