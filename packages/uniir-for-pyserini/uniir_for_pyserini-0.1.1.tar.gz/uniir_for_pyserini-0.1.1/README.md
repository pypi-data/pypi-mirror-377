# UniIR for Pyserini

[![PyPI](https://img.shields.io/pypi/v/uniir_for_pyserini?color=brightgreen)](https://pypi.org/project/uniir_for_pyserini/)
[![Downloads](https://static.pepy.tech/personalized-badge/uniir_for_pyserini?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=downloads)](https://pepy.tech/project/uniir_for_pyserini)
[![Downloads](https://static.pepy.tech/personalized-badge/uniir_for_pyserini?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=downloads/week)](https://pepy.tech/project/uniir_for_pyserini)
[![LICENSE](https://img.shields.io/badge/license-Apache-blue.svg?style=flat)](https://www.apache.org/licenses/LICENSE-2.0)

[**🌐 Homepage**](https://tiger-ai-lab.github.io/UniIR/) | [**🤗 Dataset(M-BEIR Benchmark)**](https://huggingface.co/datasets/TIGER-Lab/M-BEIR) | [**🤗 Checkpoints(UniIR models)**](https://huggingface.co/TIGER-Lab/UniIR) | [**📖 arXiv**](https://arxiv.org/pdf/2311.17136.pdf) | [**Original UniIR GitHub**](https://github.com/TIGER-AI-Lab/UniIR)

This repository contains a fork of the original UniIR codebase, modified for easy [Pyserini](https://github.com/castorini/pyserini/) integration and repackaged as a PyPI package.

`current_version = "0.1.1"`

## Installation

Install the package directly from PyPI:

```bash
pip install uniir-for-pyserini
```

Or, install from source:

```bash
git clone https://github.com/castorini/UniIR-for-Pyserini.git
cd UniIR-for-Pyserini
pip install .
```

Then, install the CLIP model:
```bash
pip install git+https://github.com/openai/CLIP.git
```

## Quick Start

The following code snippet shows how UniIR models can be used with Pyserini's encoding and indexing pipeline. In this example, `clip-sf-large` model is used to encode the `cirr_task7` corpus into dense vector representations. Similar steps can be done for on-the-fly query encoding using the QueryEncoder.

For full compatible use and features, please use/refer to these [wrapper classes](https://github.com/castorini/pyserini/blob/master/pyserini/encode/_uniir.py) in Pyserini.

```python
# Encoding and Indexing Steps
from pyserini.encode import JsonlCollectionIterator
from pyserini.encode.optional import FaissRepresentationWriter
from uniir_for_pyserini.uniir_corpus_encoder import CorpusEncoder

MBEIR_FIELDS = ['img_path', 'txt', 'modality', 'did']

mbeir_corpus_encoder = CorpusEncoder("clip_sf_large")

collection_iterator = JsonlCollectionIterator(  
    'collections/M-BEIR/mbeir_cirr_task7_cand_pool.jsonl',  
    fields=MBEIR_FIELDS,
    docid_field='did'
)

embedding_writer = FaissRepresentationWriter(
    'indexes/cirr.clip-sf-large'
)

with embedding_writer:
    for batch_info in collection_iterator(32):
        kwargs = {'fp16': True}
        for field_name in MBEIR_FIELDS:
            kwargs[f'{field_name}s'] = batch_info[field_name] 
        
        embeddings = mbeir_corpus_encoder.encode(**kwargs)
        batch_info['vector'] = embeddings
        embedding_writer.write(batch_info, MBEIR_FIELDS) 

# Searching Step
from pyserini.search.faiss import FaissSearcher
from pyserini.query_iterator import MBEIRQueryIterator
from uniir_for_pyserini.uniir_query_encoder import QueryEncoder

mbeir_query_encoder = QueryEncoder("clip_sf_large")

searcher = FaissSearcher(  
        'indexes/cirr.clip-sf-large',
        mbeir_query_encoder  
    )

query_iterator = MBEIRQueryIterator.from_topics('mbeir_cirr_task7_test.jsonl')

results = {}    
for qid, query_data in query_iterator:  
    # query_data now contains the structured M-BEIR format:  
    # {'qid', 'query_txt', 'query_img_path', 'query_modality', 'pos_cand_list'}  
      
    hits = searcher.search(query_data, k=1000) 
    results[qid] = [(hit.docid, hit.score) for hit in hits]
```

## Available Models

Note: L2 Norm isn't applied during encoding because it is applied in the UniIR wrapper classes in Pyserini

This package supports the following UniIR models from the [TIGER-Lab UniIR Hugging Face Hub](https://huggingface.co/TIGER-Lab/UniIR):

- `clip_sf_large`
- `blip_ff_large`

## Contact

For contact regarding the Pyserini integration section, please email [Sahel Sharifymoghaddam](mailto:sahel.sharifymoghaddam@uwaterloo.ca) or [Daniel Guo](mailto:daniel168.guo@gmail.com).

For contact regarding the original UniIR codebase, please email the authors of the original UniIR repository.

## Citation

If you use this work with Pyserini, please cite Pyserini in addition to the original UniIR paper:

```bibtex
@INPROCEEDINGS{wei2024uniir,
  author = "Cong Wei and Tang Chen and Haonan Chen and Hexiang Hu and Ge Zhang and Jie Fu and Alan Ritter and Wenhu Chen",
  title = "{UniIR}: Training and Benchmarking Universal Multimodal Information Retrievers",
  booktitle = "European Conference on Computer Vision",
  year = 2024,
  pages ="387--404",
}

@INPROCEEDINGS{Lin_etal_SIGIR2021_Pyserini,
   author = "Jimmy Lin and Xueguang Ma and Sheng-Chieh Lin and Jheng-Hong Yang and Ronak Pradeep and Rodrigo Nogueira",
   title = "{Pyserini}: A {Python} Toolkit for Reproducible Information Retrieval Research with Sparse and Dense Representations",
   booktitle = "Proceedings of the 44th Annual International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2021)",
   year = 2021,
   pages = "2356--2362",
}
```

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
