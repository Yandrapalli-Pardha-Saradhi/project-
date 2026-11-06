from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from app.services.embedding_service import EmbeddingService, _validate_cpu_for_onnx_artifact


def test_embedding_service_is_lazy_and_pytorch_remains_default():
    service = EmbeddingService()
    assert service.backend == "pytorch"
    assert service._model is None


def test_settings_reject_embedding_index_backend_mismatch():
    settings = SimpleNamespace(
        embedding_backend="onnx", embedding_index_backend="pytorch",
        embedding_model="model", embedding_onnx_file="model.onnx",
        embedding_max_seq_length=128, embedding_num_threads=1,
        embedding_batch_size=16, embedding_revision=None,
    )
    with pytest.raises(ValueError, match="must match"):
        EmbeddingService.from_settings(settings)


def test_onnx_batch_uses_attention_mask_and_normalizes():
    service = EmbeddingService(backend="onnx", onnx_tokenizer="tokenizers")
    service._tokenizer = SimpleNamespace(
        token_to_id=lambda token: 1,
        encode_batch=lambda texts: [
            SimpleNamespace(ids=[2, 3], attention_mask=[1, 1], type_ids=[0, 0]),
            SimpleNamespace(ids=[2], attention_mask=[1], type_ids=[0]),
        ],
    )

    class FakeSession:
        def get_inputs(self):
            return [SimpleNamespace(name=x) for x in ("input_ids", "attention_mask", "token_type_ids")]

        def run(self, outputs, feed):
            assert outputs == ["last_hidden_state"]
            assert feed["attention_mask"].tolist() == [[1, 1], [1, 0]]
            assert feed["token_type_ids"].shape == (2, 2)
            return [np.array([
                [[3.0, 0.0], [0.0, 3.0]],
                [[0.0, 4.0], [100.0, 100.0]],
            ], dtype=np.float32)]

    service._model = FakeSession()
    result = service._onnx_batch(["first", "second"])
    assert result.shape == (2, 2)
    assert np.allclose(np.linalg.norm(result, axis=1), [1.0, 1.0])
    assert np.allclose(result[1], [0.0, 1.0])


def test_onnx_embed_texts_empty_does_not_load_runtime():
    service = EmbeddingService(backend="onnx")
    assert service.embed_texts([]) == []
    assert service._model is None


def test_sentencepiece_path_maps_xlmr_ids_and_special_tokens():
    service = EmbeddingService(backend="onnx", onnx_tokenizer="sentencepiece")
    service._tokenizer = SimpleNamespace(encode=lambda text, out_type=int: [10, 0])

    class FakeSession:
        def get_inputs(self):
            return [SimpleNamespace(name=x) for x in ("input_ids", "attention_mask", "token_type_ids")]

        def run(self, outputs, feed):
            assert outputs == ["last_hidden_state"]
            assert feed["input_ids"].tolist() == [[0, 11, 3, 250001, 2]]
            assert feed["attention_mask"].tolist() == [[1, 1, 1, 1, 1]]
            return [np.ones((1, 5, 2), dtype=np.float32)]

    service._model = FakeSession()
    vector = service._onnx_batch(["example <mask>"])
    assert vector.shape == (1, 2)


def test_retrieval_rejects_embedding_backend_mismatch(tmp_path):
    from app.services.retrieval_service import RetrievalService

    onnx_service = EmbeddingService(backend="onnx")
    RetrievalService(onnx_service, str(tmp_path), "onnx_index")
    pytorch_service = EmbeddingService(backend="pytorch")
    with pytest.raises(ValueError, match="re-index"):
        RetrievalService(pytorch_service, str(tmp_path), "onnx_index")


def test_avx2_artifact_requires_x86_and_linux_cpu_flag(tmp_path):
    cpuinfo = tmp_path / "cpuinfo"
    cpuinfo.write_text("flags : sse avx avx2\n\nflags : sse avx avx2\n", encoding="utf-8")
    _validate_cpu_for_onnx_artifact("model_quint8_avx2.onnx", "Linux", "x86_64", cpuinfo)
    cpuinfo.write_text("flags : sse avx\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="AVX2 is not confirmed"):
        _validate_cpu_for_onnx_artifact("model_quint8_avx2.onnx", "Linux", "x86_64", cpuinfo)
    with pytest.raises(RuntimeError, match="runtime architecture"):
        _validate_cpu_for_onnx_artifact("model_quint8_avx2.onnx", "Linux", "aarch64", cpuinfo)
