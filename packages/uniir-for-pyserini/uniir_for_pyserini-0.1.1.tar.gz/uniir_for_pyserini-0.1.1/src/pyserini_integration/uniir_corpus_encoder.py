from typing import List

from torch.utils.data import DataLoader

from uniir_for_pyserini.pyserini_integration.uniir_base_encoder import UniIRBaseEncoder
from uniir_for_pyserini.pyserini_integration.mbeir_datasets import MBEIRCorpusDataset
from uniir_for_pyserini.data.mbeir_dataset import MBEIRCandidatePoolCollator
from uniir_for_pyserini.common.mbeir_embedder import generate_embeds_and_ids_for_dataset_with_gather
from uniir_for_pyserini.data.preprocessing.utils import format_string, hash_did


class CorpusEncoder(UniIRBaseEncoder):
    def __init__(self, model_name: str, device="cuda:0"):
        super().__init__(model_name, device)

    def encode(
        self,
        dids: List[int],
        img_paths: List[str],
        modalitys: List[str],
        txts: List[str],
        fp16: bool = False,
    ):
        batch_len = len(dids)
        batch_info = {
            "did": [hash_did(did) for did in dids],
            "img_path": img_paths,
            "modality": modalitys,
            "txt": [format_string(txt) for txt in txts],
        }
        dataset = MBEIRCorpusDataset(batch_info, self.img_preprocess_fn)
        collator = MBEIRCandidatePoolCollator(tokenizer=self.tokenizer, image_size=(224, 224))
        dataloader = DataLoader(dataset, batch_size=batch_len, collate_fn=collator)

        corpus_embeddings, _ = generate_embeds_and_ids_for_dataset_with_gather(
            self.model,
            dataloader,
            device=self.device,
            use_fp16=fp16,
        )

        return corpus_embeddings
