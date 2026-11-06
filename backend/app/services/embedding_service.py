from __future__ import annotations

import threading
import re
from pathlib import Path
from typing import Any, List, Optional

_XLMR_SPECIAL_IDS = {"<s>": 0, "<pad>": 1, "</s>": 2, "<unk>": 3, "<mask>": 250001}
_XLMR_SPECIAL_PATTERN = re.compile("(" + "|".join(re.escape(x) for x in _XLMR_SPECIAL_IDS) + ")")


def _validate_cpu_for_onnx_artifact(file_name: str, system: str, machine: str,
                                    cpuinfo_path: Path = Path("/proc/cpuinfo")) -> None:
    """Fail closed for the AVX2-specific production artifact on Linux."""
    if "avx2" not in file_name.casefold():
        return
    normalized_machine = machine.casefold()
    if normalized_machine not in {"x86_64", "amd64"}:
        raise RuntimeError(
            f"ONNX artifact {file_name!r} is the AVX2 x86 variant, "
            f"but the runtime architecture is {machine!r}"
        )
    if system.casefold() != "linux":
        return
    try:
        lines = cpuinfo_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(
            "Cannot verify AVX2 support: Linux CPU flags are unavailable at "
            f"{cpuinfo_path}"
        ) from exc
    flag_sets = [
        set(line.split(":", 1)[1].split())
        for line in lines
        if re.match(r"^(?:flags|Features)\s*:", line, re.IGNORECASE)
    ]
    if not flag_sets or not all("avx2" in flags for flags in flag_sets):
        raise RuntimeError(
            f"ONNX artifact {file_name!r} uses the AVX2 variant, "
            "but AVX2 is not confirmed for every visible Linux CPU"
        )


class EmbeddingService:
    """Lazy multilingual embedder with compatible PyTorch and ONNX runtimes.

    Both paths use the model's tokenizer, 128-token truncation, attention-mask
    mean pooling, and L2 normalization. Keep the selected backend identical to
    the backend used to build a vector collection.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        backend: str = "pytorch",
        onnx_file: str = "model_quint8_avx2.onnx",
        max_seq_length: int = 128,
        num_threads: int = 1,
        batch_size: int = 16,
        revision: Optional[str] = None,
        onnx_tokenizer: str = "sentencepiece",
        graph_optimization_level: str = "all",
    ):
        if backend not in {"pytorch", "onnx"}:
            raise ValueError("embedding backend must be 'pytorch' or 'onnx'")
        if max_seq_length < 1 or batch_size < 1 or num_threads < 1:
            raise ValueError("embedding length, batch size, and thread count must be positive")
        if onnx_tokenizer not in {"sentencepiece", "tokenizers"}:
            raise ValueError("ONNX tokenizer must be 'sentencepiece' or 'tokenizers'")
        if graph_optimization_level not in {"disable", "basic", "extended", "all"}:
            raise ValueError("invalid ONNX graph optimization level")
        self.model_name = model_name
        self.backend = backend
        self.onnx_file = onnx_file
        self.max_seq_length = max_seq_length
        self.num_threads = num_threads
        self.batch_size = batch_size
        self.revision = revision
        self.onnx_tokenizer = onnx_tokenizer
        self.graph_optimization_level = graph_optimization_level
        self._model: Any = None
        self._tokenizer: Any = None
        self._lock = threading.Lock()

    @classmethod
    def from_settings(cls, settings: Any) -> "EmbeddingService":
        if settings.embedding_backend != settings.embedding_index_backend:
            raise ValueError(
                "EMBEDDING_BACKEND must match EMBEDDING_INDEX_BACKEND; vectors from "
                "different embedding backends are not interchangeable"
            )
        return cls(
            model_name=settings.embedding_model,
            backend=settings.embedding_backend,
            onnx_file=settings.embedding_onnx_file,
            max_seq_length=settings.embedding_max_seq_length,
            num_threads=settings.embedding_num_threads,
            batch_size=settings.embedding_batch_size,
            revision=settings.embedding_revision,
            onnx_tokenizer=settings.embedding_onnx_tokenizer,
            graph_optimization_level=settings.embedding_onnx_graph_optimization_level,
        )

    def _load_pytorch(self) -> None:
        import torch
        from sentence_transformers import SentenceTransformer

        torch.set_num_threads(self.num_threads)
        model = SentenceTransformer(self.model_name, device="cpu", revision=self.revision)
        model.max_seq_length = self.max_seq_length
        self._model = model

    def _load_onnx(self) -> None:
        import platform

        import onnxruntime as ort
        from huggingface_hub import hf_hub_download

        file_name = self.onnx_file
        _validate_cpu_for_onnx_artifact(
            file_name, platform.system(), platform.machine()
        )
        if "arm" in file_name.lower() and platform.machine().lower() not in {"arm64", "aarch64"}:
            raise ValueError(f"ONNX model {file_name!r} is ARM-specific on {platform.machine()}")
        if "avx512" in file_name.lower() and "avx512" not in platform.processor().lower():
            raise ValueError(f"ONNX model {file_name!r} requires AVX-512 CPU support")
        local = Path(self.model_name)
        tokenizer_filename = (
            "sentencepiece.bpe.model" if self.onnx_tokenizer == "sentencepiece" else "tokenizer.json"
        )
        if local.is_dir():
            tokenizer_path = local / tokenizer_filename
            model_path = local / "onnx" / file_name
            if not tokenizer_path.is_file() or not model_path.is_file():
                raise FileNotFoundError(
                    f"Local model must contain {tokenizer_filename} and onnx/<configured model>"
                )
        else:
            kwargs = {"repo_id": self.model_name, "revision": self.revision}
            tokenizer_path = Path(hf_hub_download(filename=tokenizer_filename, **kwargs))
            model_path = Path(hf_hub_download(filename=f"onnx/{file_name}", **kwargs))

        if self.onnx_tokenizer == "sentencepiece":
            import sentencepiece as spm

            tokenizer = spm.SentencePieceProcessor(model_file=str(tokenizer_path))
        else:
            from tokenizers import Tokenizer

            tokenizer = Tokenizer.from_file(str(tokenizer_path))
            tokenizer.enable_truncation(max_length=self.max_seq_length)
        options = ort.SessionOptions()
        options.intra_op_num_threads = self.num_threads
        options.inter_op_num_threads = 1
        optimization_levels = {
            "disable": ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
            "basic": ort.GraphOptimizationLevel.ORT_ENABLE_BASIC,
            "extended": ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED,
            "all": ort.GraphOptimizationLevel.ORT_ENABLE_ALL,
        }
        options.graph_optimization_level = optimization_levels[self.graph_optimization_level]
        session = ort.InferenceSession(
            str(model_path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        self._tokenizer = tokenizer
        self._model = session

    @property
    def model(self) -> Any:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    if self.backend == "onnx":
                        self._load_onnx()
                    else:
                        self._load_pytorch()
        return self._model

    def _onnx_batch(self, texts: List[str]):
        import numpy as np

        if self.onnx_tokenizer == "sentencepiece":
            token_rows = []
            for text in texts:
                content = []
                for part in _XLMR_SPECIAL_PATTERN.split(text):
                    if not part:
                        continue
                    special_id = _XLMR_SPECIAL_IDS.get(part)
                    if special_id is not None:
                        content.append(special_id)
                    else:
                        content.extend(
                            3 if token_id == 0 else token_id + 1
                            for token_id in self._tokenizer.encode(part, out_type=int)
                        )
                token_rows.append([0] + content[:self.max_seq_length - 2] + [2])
            pad_id = _XLMR_SPECIAL_IDS["<pad>"]
        else:
            encodings = self._tokenizer.encode_batch(texts)
            token_rows = [row.ids for row in encodings]
            pad_id = self._tokenizer.token_to_id("<pad>")
            if pad_id is None:
                raise ValueError("Tokenizer has no <pad> token")
        width = max(len(row) for row in token_rows)
        ids = np.full((len(texts), width), pad_id, dtype=np.int64)
        mask = np.zeros((len(texts), width), dtype=np.int64)
        type_ids = np.zeros((len(texts), width), dtype=np.int64)
        for index, row in enumerate(token_rows):
            size = len(row)
            ids[index, :size] = row
            mask[index, :size] = 1
        feed = {"input_ids": ids, "attention_mask": mask}
        input_names = {item.name for item in self.model.get_inputs()}
        if "token_type_ids" in input_names:
            feed["token_type_ids"] = type_ids
        hidden = self.model.run(["last_hidden_state"], feed)[0]
        weights = mask.astype(hidden.dtype)[..., None]
        pooled = (hidden * weights).sum(axis=1) / np.maximum(weights.sum(axis=1), 1e-9)
        norms = np.linalg.norm(pooled, axis=1, keepdims=True)
        pooled = pooled / np.maximum(norms, 1e-12)
        if not np.isfinite(pooled).all():
            raise ValueError("ONNX encoder returned non-finite embeddings")
        return pooled

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.backend == "pytorch":
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return embeddings.tolist()

        import numpy as np

        # Ensure tokenizer and session are initialized together on first use.
        _ = self.model
        batches = [self._onnx_batch(texts[i:i + self.batch_size]) for i in range(0, len(texts), self.batch_size)]
        embeddings = np.concatenate(batches, axis=0)
        return embeddings.astype(np.float32, copy=False).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]
