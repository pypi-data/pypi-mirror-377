# Copyright (c) Alibaba, Inc. and its affiliates.

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field

from torch import nn
from transformers import Trainer, TrainingArguments
from transformers.trainer_pt_utils import get_parameter_names
from transformers.utils import is_sagemaker_mp_enabled
from transformers.pytorch_utils import ALL_LAYERNORM_LAYERS
# from transformers.trainer_utils import ShardedDDPOption
# from transformers.integrations import is_fairscale_available
from transformers.dependency_versions_check import dep_version_check

logger = logging.getLogger(__name__)

# if is_fairscale_available():
#     dep_version_check("fairscale")
#     import fairscale
#     from fairscale.optim import OSS

if is_sagemaker_mp_enabled():
    import smdistributed.modelparallel.torch as smp

@dataclass
class CRFTrainingArguments(TrainingArguments):
    learning_rate_ner: Optional[float] = field(default=None, metadata={"help": "Custom initial learning rate for the CRF and Linear layers on AdamW."})
    weight_decay_ner: Optional[float] = field(default=None, metadata={"help": "Custom weight decay for the CRF and Linear layers on AdamW."})

class CRFTrainer(Trainer):
    def create_optimizer(self):
        """
        Setup the optimizer.

        We provide a reasonable default that works well. If you want to use something else, you can pass a tuple in the
        Trainer's init through `optimizers`, or subclass and override this method in a subclass.
        """
        opt_model = self.model_wrapped if is_sagemaker_mp_enabled() else self.model

        if self.optimizer is None:
            """
            decay_parameters = get_parameter_names(opt_model, ALL_LAYERNORM_LAYERS)
            decay_parameters = [name for name in decay_parameters if "bias" not in name]
            optimizer_grouped_parameters = [
                {
                    "params": [
                        p for n, p in opt_model.named_parameters() if (n in decay_parameters and p.requires_grad)
                    ],
                    "weight_decay": self.args.weight_decay,
                },
                {
                    "params": [
                        p for n, p in opt_model.named_parameters() if (n not in decay_parameters and p.requires_grad)
                    ],
                    "weight_decay": 0.0,
                },
            ]
            """
            _all_parameters = get_parameter_names(opt_model, ALL_LAYERNORM_LAYERS)
            linear_crf_parameters = [name for name in _all_parameters if "classifier" in name or "crf" in name]
            decay_parameters = [name for name in _all_parameters if "bias" not in name]

            print(f'CRF parameters: {linear_crf_parameters}')

            weight_decay = self.args.weight_decay
            weight_decay_ner = self.args.weight_decay_ner if self.args.weight_decay_ner is not None else weight_decay
            learning_rate_ner = self.args.learning_rate_ner if self.args.learning_rate_ner is not None else self.args.learning_rate

            optimizer_grouped_parameters = [
                {
                    "params": [
                        p for n, p in opt_model.named_parameters() if (n in decay_parameters and n not in linear_crf_parameters and p.requires_grad)
                    ],
                    "weight_decay": weight_decay,
                },
                {
                    "params": [
                        p for n, p in opt_model.named_parameters() if (n not in decay_parameters and n not in linear_crf_parameters and p.requires_grad)
                    ],
                    "weight_decay": 0.0,
                },
                {
                    "params": [
                        p for n, p in opt_model.named_parameters() if (n in decay_parameters and n in linear_crf_parameters and p.requires_grad)
                    ],
                    "weight_decay": weight_decay_ner,
                    "lr": learning_rate_ner,
                },
                {
                    "params": [
                        p for n, p in opt_model.named_parameters() if (n not in decay_parameters and n in linear_crf_parameters and p.requires_grad)
                    ],
                    "weight_decay": 0.0,
                    "lr": learning_rate_ner,
                }
            ]

            optimizer_cls, optimizer_kwargs = Trainer.get_optimizer_cls_and_kwargs(self.args)

            # if self.sharded_ddp == ShardedDDPOption.SIMPLE:
            #     self.optimizer = OSS(
            #         params=optimizer_grouped_parameters,
            #         optim=optimizer_cls,
            #         **optimizer_kwargs,
            #     )
            # else:
            self.optimizer = optimizer_cls(optimizer_grouped_parameters, **optimizer_kwargs)
            if optimizer_cls.__name__ == "Adam8bit":
                import bitsandbytes

                manager = bitsandbytes.optim.GlobalOptimManager.get_instance()

                skipped = 0
                for module in opt_model.modules():
                    if isinstance(module, nn.Embedding):
                        skipped += sum({p.data_ptr(): p.numel() for p in module.parameters()}.values())
                        logger.info(f"skipped {module}: {skipped/2**20}M params")
                        manager.register_module_override(module, "weight", {"optim_bits": 32})
                        logger.debug(f"bitsandbytes: will optimize {module} in fp32")
                logger.info(f"skipped: {skipped/2**20}M params")

        if is_sagemaker_mp_enabled():
            self.optimizer = smp.DistributedOptimizer(self.optimizer)

        return self.optimizer

#TODO: use or discard?
def get_crf_params_groups(model: nn.Module, crf_lr = 5e-2):
    if hasattr(model, 'module'):
            model = model.module  # type ignore
    groups = [{'lr': crf_lr, 'regex': 'crf'}]
    param_groups = make_parameter_groups(model.named_parameters(), groups)
    return param_groups

# The implementation is adopted from AllenNLP and modified.
# https://github.com/allenai/allennlp/blob/main/allennlp/training/optimizers.py
# Licensed under the Apache License, Version 2.0.
def make_parameter_groups(
    model_parameters: List[Tuple[str, nn.Parameter]],  # type: ignore
    groups: Optional[List[Dict[str, Any]]] = None,
) -> Union[List[Dict[str, Any]], List[nn.Parameter]]:  # type: ignore
    """
    Takes a list of model parameters with associated names (typically coming from something like
    `model.named_parameters()`), along with a grouping (as specified below), and prepares them to be passed
    to the `__init__` function of a `torch.Optimizer`.  This means separating the parameters into
    groups with the given regexes, and prepping whatever keyword arguments are given for those
    regexes in `groups`.
    `groups` contains something like:
    ```
    [
        { 'regex': "transformer_model", 'lr': 1e-3 },
        { 'regex': ['re1', 're2', 're3'], 'lr': 1e-4 }
    ]
    ```
    All of key-value pairs specified in each of these dictionaries will passed passed as-is
    to the optimizer, with the exception of a dictionaries that specify `requires_grad` to be `False`:
    ```
    [
        ...
        {'regex': 'regex', 'requires_grad': False }
    ]
    ```
    When a parameter group has `{"requires_grad": False}`, the gradient on all matching parameters
    will be disabled and that group will be dropped so that it's not actually passed to the optimizer.
    Ultimately, the return value of this function is in the right format to be passed directly
    as the `params` argument to a pytorch `Optimizer`.
    If there are multiple groups specified, this is a list of dictionaries, where each
    dict contains a "parameter group" and groups specific options, e.g., {'params': [list of
    parameters], 'lr': 1e-3, ...}.  Any config option not specified in the additional options (e.g.
    for the default group) is inherited from the top level arguments given in the constructor.  See:
    <https://pytorch.org/docs/0.3.0/optim.html?#per-parameter-options>.  See also our
    `test_optimizer_parameter_groups` test for an example of how this works in this code.
    The dictionary's return type is labeled as `Any`, because it can be a `List[torch.nn.Parameter]`
    (for the "params" key), or anything else (typically a float) for the other keys.
    """
    if groups:
        # reformat eache group to ('regex', {})
        allennlp_groups = list()
        for k, group_regexes in enumerate(groups):
            regexes = group_regexes.pop('regex')
            if isinstance(regexes, str):
                regexes = [regexes]
            if not isinstance(regexes, list):
                raise ValueError(f'Unsopported regex: {regexes}')
            allennlp_groups.append((regexes, group_regexes))
        groups = allennlp_groups

        # In addition to any parameters that match group specific regex,
        # we also need a group for the remaining "default" group.
        # Those will be included in the last entry of parameter_groups.
        parameter_groups: Union[List[Dict[str, Any]], List[nn.Parameter]] = [  # type: ignore
            {'params': []} for _ in range(len(groups) + 1)
        ]
        # add the group specific kwargs
        for k in range(len(groups)):
            parameter_groups[k].update(groups[k][1])  # type: ignore

        regex_use_counts: Dict[str, int] = {}
        parameter_group_names: List[set] = [set() for _ in range(len(groups) + 1)]
        for name, param in model_parameters:
            # Determine the group for this parameter.
            group_index = None
            for k, group_regexes in enumerate(groups):
                for regex in group_regexes[0]:  # type: ignore
                    if regex not in regex_use_counts:
                        regex_use_counts[regex] = 0
                    if re.search(regex, name):
                        if group_index is not None and group_index != k:
                            raise ValueError(
                                '{} was specified in two separate parameter groups'.format(name)
                            )
                        group_index = k
                        regex_use_counts[regex] += 1

            if group_index is not None:
                parameter_groups[group_index]['params'].append(param)
                parameter_group_names[group_index].add(name)
            else:
                # the default group
                parameter_groups[-1]['params'].append(param)
                parameter_group_names[-1].add(name)

        # find and remove any groups with 'requires_grad = False'
        no_grad_group_indices: List[int] = []
        for k, (names, group) in enumerate(zip(parameter_group_names, parameter_groups)):
            if group.get('requires_grad') is False:
                no_grad_group_indices.append(k)
                logger.info(
                    'Disabling gradient for the following parameters: %s',
                    json.dumps(sorted(names), indent=2),
                )
                for param in group['params']:
                    param.requires_grad_(False)

                # warn about any other unused options in that group.
                unused_options = {
                    key: val for key, val in group.items() if key not in ('params', 'requires_grad')
                }
                if unused_options:
                    logger.warning(
                        'Ignoring unused options %s for %s',
                        unused_options,
                        json.dumps(sorted(names), indent=2),
                    )
        parameter_group_names = [
            names
            for (k, names) in enumerate(parameter_group_names)
            if k not in no_grad_group_indices
        ]
        parameter_groups = [
            group for (k, group) in enumerate(parameter_groups) if k not in no_grad_group_indices
        ]

        # log the remaining parameter groups
        logger.info('Done constructing parameter groups.')
        for k in range(len(parameter_groups)):
            group_options = {
                key: val for key, val in parameter_groups[k].items() if key != 'params'
            }
            name_string = json.dumps(sorted(parameter_group_names[k]), indent=2)
            logger.info('Group %s: %s, %s', k, group_options, name_string)

        # check for unused regex
        for regex, count in regex_use_counts.items():
            if count == 0:
                logger.warning(
                    'When constructing parameter groups, %s does not match any parameter name',
                    regex,
                )
    else:
        parameter_groups = [param for name, param in model_parameters]

    # Log the number of parameters to optimize
    num_parameters = 0
    for parameter_group in parameter_groups:
        if isinstance(parameter_group, dict):
            num_parameters += sum(parameter.numel() for parameter in parameter_group['params'])
        else:
            num_parameters += parameter_group.numel()  # type: ignore
    logger.info('Number of trainable parameters: %s', num_parameters)

    # Move the default group to the first, since `modelscope` only log lr of the first group.
    # This is the fastest way I think.
    parameter_groups.reverse()

    return parameter_groups
