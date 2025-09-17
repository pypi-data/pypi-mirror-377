# Copyright 2025 - Pruna AI GmbH. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import copy
import json
import shutil
import tempfile
from enum import Enum
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

import torch
import transformers
from huggingface_hub import ModelCard, ModelCardData, login, repo_exists, upload_large_folder

from pruna.config.smash_config import SMASH_CONFIG_FILE_NAME
from pruna.engine.load import (
    LOAD_FUNCTIONS,
    PICKLED_FILE_NAME,
    PIPELINE_INFO_FILE_NAME,
    SAVE_BEFORE_SMASH_CACHE_DIR,
)
from pruna.engine.model_checks import get_helpers
from pruna.engine.utils import ModelContext, determine_dtype
from pruna.logging.logger import pruna_logger

if TYPE_CHECKING:
    from pruna.config.smash_config import SmashConfig
    from pruna.engine.pruna_model import PrunaModel


def save_pruna_model(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the model to the specified directory.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    model_path = Path(model_path)
    if not model_path.exists():
        model_path.mkdir(parents=True, exist_ok=True)

    if SAVE_FUNCTIONS.torch_artifacts.name in smash_config.save_fns:
        save_torch_artifacts(model, model_path, smash_config)
        smash_config.save_fns.remove(SAVE_FUNCTIONS.torch_artifacts.name)

    # in the case of no specialized save functions, we use the model's original save function
    if len(smash_config.save_fns) == 0:
        pruna_logger.debug("Using model's original save function...")
        save_fn = original_save_fn

    # if save-before-move was the last operation, we simply move the already saved files, we have delt with them before
    elif smash_config.save_fns[-1] == SAVE_FUNCTIONS.save_before_apply.name:
        pruna_logger.debug("Moving saved model...")
        save_fn = save_before_apply

    # if the original save function was overwritten *once*, we can use the new save function
    elif len(smash_config.save_fns) == 1:
        pruna_logger.debug(f"Using new save function {smash_config.save_fns[-1]}...")
        save_fn = SAVE_FUNCTIONS[smash_config.save_fns[-1]]
        pruna_logger.debug(
            f"Overwriting original load function {smash_config.load_fns} with {smash_config.save_fns[-1]}..."
        )

    # in the case of multiple, specialized save functions, we default to pickled
    else:
        pruna_logger.debug(f"Several save functions stacked: {smash_config.save_fns}, defaulting to pickled")
        save_fn = SAVE_FUNCTIONS.pickled
        smash_config.load_fns = [LOAD_FUNCTIONS.pickled.name]

    # execute selected save function
    save_fn(model, model_path, smash_config)

    # save smash config (includes tokenizer and processor)
    smash_config.save_to_json(model_path)


def save_pruna_model_to_hub(
    instance: "PrunaModel" | Any,
    model: Any,
    smash_config: "SmashConfig" | Any,
    repo_id: str,
    model_path: str | Path | None = None,
    *,
    revision: str | None = None,
    private: bool = False,
    allow_patterns: List[str] | str | None = None,
    ignore_patterns: List[str] | str | None = None,
    num_workers: int | None = None,
    print_report: bool = True,
    print_report_every: int = 60,
    hf_token: str | None = None,
) -> None:
    """
    Save the model to the Hugging Face Hub.

    Parameters
    ----------
    instance : PrunaModel | Any
        The PrunaModel instance to save.
    model : Any
        The model to save.
    smash_config : Union[SmashConfig, Any]
        The SmashConfig object containing the save and load functions.
    repo_id : str
        The repository ID.
    model_path : str | Path | None, optional
        The path to the directory where the model will be saved.
    revision : str | None, optional
        The revision of the model.
    private : bool, optional
        Whether the model is private.
    allow_patterns : List[str] | str | None, optional
        The allow patterns.
    ignore_patterns : List[str] | str | None, optional
        The ignore patterns.
    num_workers : int | None, optional
        The number of workers.
    print_report : bool, optional
        Whether to print the report.
    print_report_every : int, optional
        The print report every.
    hf_token : str | None
        The Hugging Face token to use for authentication to push models to the Hub.
    """
    # Create a temporary directory within the specified folder path to store the model files
    with tempfile.TemporaryDirectory() as temp_dir:
        # If no model_path is provided, use the temporary directory
        model_path = model_path or temp_dir
        model_path_pathlib = Path(model_path)

        # Save the model and its configuration to the temporary directory
        save_pruna_model(model=model, model_path=model_path, smash_config=smash_config)

        # Load the smash config
        with (model_path_pathlib / SMASH_CONFIG_FILE_NAME).open() as f:
            smash_config_data = json.load(f)

        # Load the base model card if repo exists on Hub
        model_name_or_path = getattr(model, "name_or_path", None)
        if model_name_or_path is not None and repo_exists(repo_id=str(model_name_or_path), repo_type="model"):
            model_card_data = ModelCard.load(repo_id_or_path=model.name_or_path, repo_type="model", token=hf_token).data
        else:
            model_card_data = ModelCardData()
            if "diffusers" in model.__module__:
                model_card_data["library_name"] = "diffusers"
            elif "transformers" in model.__module__:
                model_card_data["library_name"] = "transformers"

        # Format the content for the README using the template and the loaded configuration data
        template_path = Path(__file__).parent / "hf_hub_utils" / "model_card_template.md"
        # Get the pruna library version from initalized module as OSS or paid so we can use the same method for both
        pruna_library = instance.__module__.split(".")[0] if "." in instance.__module__ else None
        model_card_data["tags"] = list({f"{pruna_library}-ai", "safetensors", "pruna-ai"})
        # Build the template parameters dictionary for clarity and maintainability
        template_params: dict = {
            "repo_id": repo_id,
            "base_repo_id": model_name_or_path,
            "smash_config": json.dumps(smash_config_data, indent=4),
            "library_name": model_card_data.library_name,
            "pruna_model_class": instance.__class__.__name__,
            "pruna_library": pruna_library,
        }
        # Remove any parameters with None values to avoid passing them to the template
        template_params = {k: v for k, v in template_params.items() if v is not None}

        model_card = ModelCard.from_template(
            card_data=model_card_data,
            template_path=str(template_path),
            **template_params,
        )
        model_card.save(model_path_pathlib / "README.md")

        # Upload the contents of the temporary directory to the specified repository on the hub
        if hf_token:
            login(token=hf_token)
        upload_large_folder(
            repo_id=repo_id,
            folder_path=model_path_pathlib,
            repo_type="model",
            revision=revision,
            private=private,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            num_workers=num_workers,
            print_report=print_report,
            print_report_every=print_report_every,
        )


def original_save_fn(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the model to the specified directory.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    # catch any huggingface diffuser or transformer model and record which load function to use
    if "diffusers" in model.__module__:
        if LOAD_FUNCTIONS.diffusers.name not in smash_config.load_fns:
            smash_config.load_fns.append(LOAD_FUNCTIONS.diffusers.name)
        model.save_pretrained(model_path)
        # save dtype of the model as diffusers does not provide this at the moment
        dtype = determine_dtype(model)
        # save dtype
        dtype_info_path = Path(model_path) / "dtype_info.json"
        with dtype_info_path.open("w") as f:
            json.dump({"dtype": str(dtype).split(".")[-1]}, f)

    elif "transformers" in model.__module__:
        if LOAD_FUNCTIONS.transformers.name not in smash_config.load_fns:
            smash_config.load_fns.append(LOAD_FUNCTIONS.transformers.name)
        model.save_pretrained(model_path)

        # if the model is a transformers pipeline, we additionally save the pipeline info
        if isinstance(model, transformers.Pipeline):
            save_pipeline_info(model, model_path)

    # otherwise, resort to pickled saving
    else:
        save_pickled(model, model_path, smash_config)
        smash_config.load_fns.append(LOAD_FUNCTIONS.pickled.name)


def save_pipeline_info(pipeline_obj: Any, save_directory: str | Path) -> None:
    """
    Save pipeline information to a JSON file in the specified directory for easy loading.

    Parameters
    ----------
    pipeline_obj : Any
        The pipeline object to save.
    save_directory : str | Path
        The directory to save the pipeline information to.
    """
    pruna_logger.info(f"Detected pipeline, saving info to {PIPELINE_INFO_FILE_NAME}")
    info = {
        "pipeline_type": type(pipeline_obj).__name__,
        "task": pipeline_obj.task,
    }

    filepath = Path(save_directory) / PIPELINE_INFO_FILE_NAME

    with filepath.open("w") as fp:
        json.dump(info, fp)


def save_before_apply(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the model by moving already saved, temporary files into the model path.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    save_dir = Path(smash_config.cache_dir) / SAVE_BEFORE_SMASH_CACHE_DIR

    # load old smash config to get load_fn assigned previously
    # load json directly from file
    smash_config_path = save_dir / SMASH_CONFIG_FILE_NAME
    with smash_config_path.open("r") as f:
        old_smash_config = json.load(f)

    smash_config.load_fns.extend(old_smash_config["load_fns"])
    smash_config.load_fns = list(set(smash_config.load_fns))
    del old_smash_config

    # move files in save dir into model path
    for file in save_dir.iterdir():
        target_path = Path(model_path) / file.name
        if target_path == file:
            continue
        if file.is_file():
            shutil.copy(file, target_path)
        else:
            shutil.copytree(file, target_path)


def save_pickled(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the model by pickling it.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    # helpers can not be pickled, we will disable and just reapply them later
    smash_helpers = get_helpers(model)
    for helper in smash_helpers:
        getattr(model, helper).disable()
    torch.save(model, Path(model_path) / PICKLED_FILE_NAME)
    smash_config.load_fns.append(LOAD_FUNCTIONS.pickled.name)


def save_model_hqq(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the model with HQQ functionality.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    # make sure to save the pipeline along with the tokenizer
    if isinstance(model, transformers.Pipeline):
        if model.tokenizer is not None:
            model.tokenizer.save_pretrained(model_path)
        save_model_hqq(model.model, model_path, smash_config)
        return

    from pruna.algorithms.quantization.hqq import HQQQuantizer

    algorithm_packages = HQQQuantizer().import_algorithm_packages()

    # we need to create a separate path for the quantized model
    if hasattr(model, "model") and hasattr(model.model, "language_model"):
        quantized_path = Path(model_path) / "hqq_language_model"
    else:
        quantized_path = Path(model_path)

    # save the quantized model only.
    with ModelContext(model, read_only=True) as (_, working_model):
        if isinstance(working_model, algorithm_packages["HQQModelForCausalLM"]):
            working_model.save_quantized(quantized_path)
        else:
            algorithm_packages["AutoHQQHFModel"].save_quantized(working_model, str(quantized_path))

    # save the rest of the model, if it is a janus like model,
    # and add a config file to the quantized model path.
    if hasattr(model, "model") and hasattr(model.model, "language_model"):
        transformer_backup = model.model.language_model
        model.model.language_model = None
        model.save_pretrained(model_path)
        # Create a copy to avoid modifying the original config
        hqq_config = copy.deepcopy(model.config.text_config)
        # for re-loading the model, hqq expects the architecture to be LlamaForCausalLM
        hqq_config.architectures = ["LlamaForCausalLM"]

        quantized_path.mkdir(parents=True, exist_ok=True)

        config_path = quantized_path / "config.json"
        with config_path.open("w") as f:
            json.dump(hqq_config.to_dict(), f, indent=2)

        model.model.language_model = transformer_backup

    smash_config.load_fns.append(LOAD_FUNCTIONS.hqq.name)


def save_model_hqq_diffusers(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the pipeline by saving the quantized model with HQQ, and rest of the pipeline with diffusers.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    from pruna.algorithms.quantization.hqq_diffusers import (
        HQQDiffusersQuantizer,
        construct_base_class,
    )

    pruna_logger.warning(
        "Currently HQQ can only save linear layers. So model (e.g. Sana) with separate torch.nn.Parameters or "
        "buffers will be partially saved."
    )

    model_path = Path(model_path)

    hf_quantizer = HQQDiffusersQuantizer()
    auto_hqq_hf_diffusers_model = construct_base_class(hf_quantizer.import_algorithm_packages())

    with (model_path / "dtype_info.json").open("w") as f:
        json.dump({"dtype": str(model.dtype).split(".")[-1]}, f)

    if hasattr(model, "transformer"):
        # save the backbone
        auto_hqq_hf_diffusers_model.save_quantized(model.transformer, model_path / "backbone_quantized")
        transformer_backup = model.transformer
        model.transformer = None
        # save the rest of the pipeline
        model.save_pretrained(model_path)
        model.transformer = transformer_backup
    elif hasattr(model, "unet"):
        # save the backbone
        auto_hqq_hf_diffusers_model.save_quantized(model.unet, model_path / "backbone_quantized")
        unet_backup = model.unet
        model.unet = None
        # save the rest of the pipeline
        model.save_pretrained(model_path)
        model.unet = unet_backup
    else:
        auto_hqq_hf_diffusers_model.save_quantized(model, model_path)
    smash_config.load_fns.append(LOAD_FUNCTIONS.hqq_diffusers.name)


def save_torch_artifacts(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Save the model by saving the torch artifacts.

    Parameters
    ----------
    model : Any
        The model to save.
    model_path : str | Path
        The directory to save the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    artifacts = torch.compiler.save_cache_artifacts()

    assert artifacts is not None
    artifact_bytes, cache_info = artifacts

    # check if the bytes are empty
    if artifact_bytes == b"\x00\x00\x00\x00\x00\x00\x00\x01":
        pruna_logger.error(
            "Model has not been run before. Please run the model before saving to construct the compilation graph."
        )

    artifact_path = Path(model_path) / "artifact_bytes.bin"
    artifact_path.write_bytes(artifact_bytes)

    smash_config.load_fns.append(LOAD_FUNCTIONS.torch_artifacts.name)


def reapply(model: Any, model_path: str | Path, smash_config: SmashConfig) -> None:
    """
    Reapply the model.

    Parameters
    ----------
    model : Any
        The model to reapply.
    model_path : str | Path
        The directory to reapply the model to.
    smash_config : SmashConfig
        The SmashConfig object containing the save and load functions.
    """
    raise ValueError("Reapply function is not a save function to call directly")


class SAVE_FUNCTIONS(Enum):  # noqa: N801
    """
    Enumeration of save functions for different model types.

    This enum provides callable functions for saving different types of models,
    including pickled models, IPEX LLM models, HQQ models, and models that need
    to be saved before applying transformations.

    Parameters
    ----------
    value : callable
        The save function to be called.
    names : str
        The name of the enum member.
    module : str
        The module where the enum is defined.
    qualname : str
        The qualified name of the enum.
    type : type
        The type of the enum.
    start : int
        The start index for auto-numbering enum values.

    Examples
    --------
    >>> SAVE_FUNCTIONS.pickled(model, save_path, smash_config)
    # Model saved to disk in pickled format
    """

    pickled = partial(save_pickled)
    hqq = partial(save_model_hqq)
    hqq_diffusers = partial(save_model_hqq_diffusers)
    save_before_apply = partial(save_before_apply)
    reapply = partial(reapply)
    torch_artifacts = partial(save_torch_artifacts)

    def __call__(self, *args, **kwargs) -> None:
        """
        Call the save function.

        Parameters
        ----------
        args : Any
            The arguments to pass to the save function.
        kwargs : Any
            The keyword arguments to pass to the save function.
        """
        if self.value is not None:
            self.value(*args, **kwargs)
