import yaml
import random
from typing import Optional

import pandas as pd
from torch.utils.data import DataLoader

from uniir_for_pyserini.pyserini_integration.uniir_base_encoder import UniIRBaseEncoder
from uniir_for_pyserini.pyserini_integration.mbeir_datasets import MBEIRQueryDataset
from uniir_for_pyserini.data.mbeir_dataset import MBEIRInferenceOnlyCollator
from uniir_for_pyserini.common.mbeir_embedder import generate_embeds_and_ids_for_dataset_with_gather
from uniir_for_pyserini.data.preprocessing.utils import format_string, hash_qid


class QueryEncoder(UniIRBaseEncoder):
    def __init__(
        self,
        model_name: str,
        device="cuda:0",
    ):
        super().__init__(model_name, device)

    def _load_instruction_config(self, instruction_config):
        try:
            with open(instruction_config, "r") as f:
                config = yaml.safe_load(f)
            instruction_file = config.get("instruction_file", None)
            candidate_modality = config.get("candidate_modality", None)
            dataset_id = config.get("dataset_id", None)
            randomize_instructions = config.get("randomize_instructions", False)
            if not instruction_file or not candidate_modality or not dataset_id:
                raise ValueError(
                    "Instruction file, candidate_modality, or dataset_id is missing in the config. Please download the instruction file from https://huggingface.co/datasets/TIGER-Lab/M-BEIR/blob/main/instructions/query_instructions.tsv"
                )
        except Exception as e:
            raise ValueError(f"Error loading instruction config: {e}")

        try:
            df = pd.read_csv(instruction_file, sep="\t")
            filtered = df[df["dataset_id"].astype(int) == int(dataset_id)]
            instructions = filtered.to_dict(orient="records")

            return instructions, candidate_modality, randomize_instructions
        except Exception as e:
            raise ValueError(
                f"Error reading instruction or corpus file: {e}. Please download the instruction file from https://huggingface.co/datasets/TIGER-Lab/M-BEIR/blob/main/instructions/query_instructions.tsv"
            )

    def _get_instruction_prompt(self, instructions, c_modality, q_modality, randomize_instructions) -> Optional[str]:
        for instruction in instructions:
            if instruction["query_modality"] == q_modality and instruction["cand_modality"] == c_modality:
                if randomize_instructions:
                    prompts = [instruction[k] for k in instruction if k.startswith("prompt_")]
                    return random.choice(prompts) if prompts else None
                else:
                    return instruction["prompt_1"]

    def encode(
        self,
        qid: int,
        query_txt: str,
        query_img_path: str,
        query_modality: str,
        instruction_config: Optional[str] = None,
        fp16: bool = False,
    ):
        if instruction_config:
            instructions, candidate_modality, randomize_instructions = self._load_instruction_config(instruction_config)
            prompt = self._get_instruction_prompt(
                instructions=instructions,
                c_modality=candidate_modality,
                q_modality=query_modality,
                randomize_instructions=randomize_instructions,
            )
            if prompt is not None:
                query_txt = f"{prompt} {query_txt}" if query_txt else prompt

        query_info = [
            {
                "qid": hash_qid(qid),
                "query_txt": format_string(query_txt),
                "query_img_path": query_img_path,
                "query_modality": query_modality,
            }
        ]

        dataset = MBEIRQueryDataset(query_info, self.img_preprocess_fn)
        collator = MBEIRInferenceOnlyCollator(tokenizer=self.tokenizer, image_size=(224, 224))
        dataloader = DataLoader(dataset, batch_size=1, collate_fn=collator)

        query_embeddings, _ = generate_embeds_and_ids_for_dataset_with_gather(
            self.model,
            dataloader,
            device=self.device,
            use_fp16=fp16,
        )

        return query_embeddings
