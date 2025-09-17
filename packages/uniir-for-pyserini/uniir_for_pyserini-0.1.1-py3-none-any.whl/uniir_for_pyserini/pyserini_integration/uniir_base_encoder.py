import yaml
from types import SimpleNamespace
from abc import ABC, abstractmethod
from typing import Any
from importlib.resources import files

import torch
from huggingface_hub import hf_hub_download

from uniir_for_pyserini.models.uniir_blip.blip_featurefusion.blip_ff import BLIPFeatureFusion
from uniir_for_pyserini.models.uniir_blip.blip_scorefusion.blip_sf import BLIPScoreFusion
from uniir_for_pyserini.models.uniir_clip.clip_featurefusion.clip_ff import CLIPFeatureFusion
from uniir_for_pyserini.models.uniir_clip.clip_scorefusion.clip_sf import CLIPScoreFusion


MODEL_REGISTRY = {
    "clip_ff": (CLIPFeatureFusion, "CLIP_FF"),
    "clip_sf": (CLIPScoreFusion, "CLIP_SF"),
    "blip_ff": (BLIPFeatureFusion, "BLIP_FF"),
    "blip_sf": (BLIPScoreFusion, "BLIP_SF"),
}


class UniIRBaseEncoder(ABC):
    def __init__(self, model_name: str, device="cuda:0"):
        config_path = files("uniir_for_pyserini.pyserini_integration").joinpath("model_config.yaml")

        with config_path.open("r") as f:
            config_data = yaml.safe_load(f)

        model_key = next((key for key in MODEL_REGISTRY if key in model_name), None)
        if not model_key:
            raise ValueError(f"Unsupported model name for UniIR: {model_name}")

        ModelClass, model_dir = MODEL_REGISTRY[model_key]
        if "clip" in model_name:
            config = config_data["clip"]["large"] if "large" in model_name else config_data["clip"]["base"]
            config["device"] = device
        elif "blip" in model_name:
            config = config_data["blip"]["large"] if "large" in model_name else config_data["blip"]["base"]
            config_obj = SimpleNamespace(**config["config"])
            blip_config = files("uniir_for_pyserini.models.uniir_blip.backbone.configs").joinpath("med_config.json")
            config["config"] = config_obj
            config["med_config"] = str(blip_config)
        else:
            raise ValueError(f"Unsupported model type for UniIR: {model_name}")
        model = ModelClass(**config)

        try:
            checkpoint_path = hf_hub_download(
                repo_id="TIGER-Lab/UniIR",
                filename=f"checkpoint/{model_dir}/{model_name}.pth",
            )
        except Exception as e:
            raise ValueError(
                f"Model checkpoint not found: {e}. Please check the model name or ensure the model is available on Hugging Face Hub: https://huggingface.co/TIGER-Lab/UniIR/tree/main/checkpoint."
            )

        model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=False)["model"])
        model.float()
        model.eval()
        model = model.to(device)

        self.model = model
        self.img_preprocess_fn = model.get_img_preprocess_fn()
        self.tokenizer = model.get_tokenizer()
        self.device = device

    @abstractmethod
    def encode(self, **kwargs: Any):
        pass
