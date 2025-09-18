import logging
from typing import Generator

import torch
import vllm.entrypoints.cli.main
from vllm.config import ModelConfig, VllmConfig
from vllm.distributed import get_tensor_model_parallel_rank
from vllm.model_executor.model_loader import get_model, register_model_loader
from vllm.model_executor.model_loader.default_loader import DefaultModelLoader
from vllm.model_executor.model_loader.sharded_state_loader import ShardedStateLoader
from vllm.model_executor.model_loader.utils import set_default_torch_dtype

from ..config import (
    LOCAL_MODEL_PATH,
    REMOTE_MODEL_PATH,
    STREAM_SAFETENSORS,
)
from ..loader import SafeTensorsStreamer, prefetch, prefix_exists

logger = logging.getLogger(__name__)


@register_model_loader("union-streaming")
class UnionModelLoader(DefaultModelLoader):
    def _get_weights_iterator(self, source) -> Generator[tuple[str, torch.Tensor], None, None]:
        # Try to load weights using the Union SafeTensorsLoader. Fallback to the default loader otherwise.
        try:
            streamer = SafeTensorsStreamer(REMOTE_MODEL_PATH, LOCAL_MODEL_PATH)
        except ValueError:
            return super()._get_weights_iterator(source)
        else:
            for name, tensor in streamer.get_tensors():
                yield source.prefix + name, tensor

    def download_model(self, model_config: ModelConfig) -> None:
        # Stream only
        pass

    def _load_sharded_model(self, vllm_config: VllmConfig, model_config: ModelConfig) -> torch.nn.Module:
        # Forked from: https://github.com/vllm-project/vllm/blob/99d01a5e3d5278284bad359ac8b87ee7a551afda/vllm/model_executor/model_loader/loader.py#L613
        # Sanity checks
        tensor_parallel_size = vllm_config.parallel_config.tensor_parallel_size
        rank = get_tensor_model_parallel_rank()
        if rank >= tensor_parallel_size:
            raise ValueError(f"Invalid rank {rank} for tensor parallel size {tensor_parallel_size}")
        with set_default_torch_dtype(vllm_config.model_config.dtype):
            with torch.device(vllm_config.device_config.device):
                model = get_model(vllm_config=vllm_config, model_config=model_config)
                for _, module in model.named_modules():
                    quant_method = getattr(module, "quant_method", None)
                    if quant_method is not None:
                        quant_method.process_weights_after_loading(module)
            state_dict = ShardedStateLoader._filter_subtensors(model.state_dict())
            streamer = SafeTensorsStreamer(
                REMOTE_MODEL_PATH,
                LOCAL_MODEL_PATH,
                rank=rank,
                tensor_parallel_size=tensor_parallel_size,
            )
            for name, tensor in streamer.get_tensors():
                # If loading with LoRA enabled, additional padding may
                # be added to certain parameters. We only load into a
                # narrowed view of the parameter data.
                param_data = state_dict[name].data
                param_shape = state_dict[name].shape
                for dim, size in enumerate(tensor.shape):
                    if size < param_shape[dim]:
                        param_data = param_data.narrow(dim, 0, size)
                if tensor.shape != param_shape:
                    logger.warning(
                        "loading tensor of shape %s into parameter '%s' of shape %s",
                        tensor.shape,
                        name,
                        param_shape,
                    )
                param_data.copy_(tensor)
                state_dict.pop(name)
            if state_dict:
                raise ValueError(f"Missing keys {tuple(state_dict)} in loaded state!")
        return model.eval()

    def load_model(
        self,
        vllm_config: VllmConfig,
        model_config: ModelConfig,
    ) -> torch.nn.Module:
        logger.info("Loading model with UnionModelLoader")
        if vllm_config.parallel_config.tensor_parallel_size > 1:
            return self._load_sharded_model(vllm_config)
        else:
            return super().load_model(vllm_config, model_config)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Prefetch the model
    if REMOTE_MODEL_PATH:
        if not prefix_exists(REMOTE_MODEL_PATH):
            raise FileNotFoundError(f"Model path not found: {REMOTE_MODEL_PATH}")

        prefetch(
            REMOTE_MODEL_PATH,
            LOCAL_MODEL_PATH,
            exclude_safetensors=STREAM_SAFETENSORS,
        )

    vllm.entrypoints.cli.main.main()
