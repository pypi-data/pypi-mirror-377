# SPDX-License-Identifier: Apache-2.0
# Standard
from collections import OrderedDict
from concurrent.futures import Future
from typing import TYPE_CHECKING, Generator, List, Optional, Sequence
import asyncio
import functools
import threading

# Third Party
import torch

# First Party
from lmcache.config import LMCacheEngineMetadata
from lmcache.logging import init_logger
from lmcache.utils import (
    CacheEngineKey,
    _lmcache_nvtx_annotate,
    start_loop_in_thread_with_exceptions,
)
from lmcache.v1.config import LMCacheEngineConfig
from lmcache.v1.event_manager import EventManager, EventStatus, EventType
from lmcache.v1.lookup_server import LookupServerInterface
from lmcache.v1.memory_management import (
    MemoryAllocatorInterface,
    MemoryFormat,
    MemoryObj,
)
from lmcache.v1.storage_backend import CreateStorageBackends
from lmcache.v1.storage_backend.abstract_backend import (
    AllocatorBackendInterface,
    StorageBackendInterface,
)
from lmcache.v1.storage_backend.local_cpu_backend import LocalCPUBackend
from lmcache.v1.storage_backend.storage_backend_listener import StorageBackendListener

if TYPE_CHECKING:
    # First Party
    from lmcache.v1.cache_controller.worker import LMCacheWorker
    from lmcache.v1.lookup_client.lmcache_async_lookup_client import (
        LMCacheAsyncLookupServer,
    )

logger = init_logger(__name__)


# TODO: extend this class to implement caching policies and eviction policies
class StorageManager:
    """
    The StorageManager is responsible for managing the storage backends.
    """

    class _CPUDiskListener(StorageBackendListener):
        def __init__(self, storage_manager: "StorageManager"):
            self.storage_manager = storage_manager

        def on_evict(
            self, backend: StorageBackendInterface, keys: List[CacheEngineKey]
        ):
            """
            remove keys from lookup server only if they don't exist in local backends.

            :param StorageBackendInterface backend: The backend that evicted the keys.
            :param List[CacheEngineKey] keys: The keys that were evicted.
            """
            if self.storage_manager.lookup_server is None:
                return

            search_range = ["LocalCPUBackend", "LocalDiskBackend"]
            if str(backend) in search_range:
                search_range.remove(str(backend))

            keys_to_remove = []
            for key in keys:
                if not self.storage_manager.contains(key, search_range=search_range):
                    keys_to_remove.append(key)

            if keys_to_remove:
                self.storage_manager.lookup_server.batched_remove(keys_to_remove)

    def __init__(
        self,
        config: LMCacheEngineConfig,
        metadata: LMCacheEngineMetadata,
        allocator: MemoryAllocatorInterface,
        event_manager: EventManager,
        lmcache_worker: Optional["LMCacheWorker"] = None,
        lookup_server: Optional[LookupServerInterface] = None,
    ):
        self.loop = asyncio.new_event_loop()

        self.thread = threading.Thread(
            target=start_loop_in_thread_with_exceptions,
            args=(self.loop,),
            name="storage-manger-event-loop",
        )
        self.thread.start()

        dst_device = "cuda"
        self.storage_backends: OrderedDict[str, StorageBackendInterface] = (
            CreateStorageBackends(
                config,
                metadata,
                self.loop,
                allocator,
                dst_device,
                lmcache_worker,
                lookup_server,
            )
        )

        self.enable_nixl = config.enable_nixl

        self.allocator_backend = self._get_allocator_backend(config)
        if config.local_cpu:
            self.local_cpu_backend = self.storage_backends["LocalCPUBackend"]

        self.manager_lock = threading.Lock()

        self.lookup_server = lookup_server

        self.lmcache_worker = lmcache_worker
        self.instance_id = config.lmcache_instance_id
        self.worker_id = metadata.worker_id

        self.event_manager = event_manager

        self.async_lookup_server: Optional["LMCacheAsyncLookupServer"] = None

        self.nixl_offload_stream = torch.cuda.Stream()

        self._cpu_disk_listener = self._CPUDiskListener(self)
        if "LocalCPUBackend" in self.storage_backends:
            self.storage_backends["LocalCPUBackend"].set_listener(
                self._cpu_disk_listener
            )
        if "LocalDiskBackend" in self.storage_backends:
            self.storage_backends["LocalDiskBackend"].set_listener(
                self._cpu_disk_listener
            )

    def post_init(self, **kwargs) -> None:
        if "async_lookup_server" in kwargs:
            self.async_lookup_server = kwargs.pop("async_lookup_server")

    def _get_allocator_backend(
        self, config: LMCacheEngineConfig
    ) -> AllocatorBackendInterface:
        if self.enable_nixl:
            allocator_backend = self.storage_backends["NixlBackend"]
        else:
            allocator_backend = self.storage_backends["LocalCPUBackend"]
        assert isinstance(allocator_backend, AllocatorBackendInterface)
        return allocator_backend

    @_lmcache_nvtx_annotate
    def allocate(
        self,
        shape: torch.Size,
        dtype: torch.dtype,
        fmt: MemoryFormat = MemoryFormat.KV_2LTD,
        eviction=True,
        busy_loop=True,
    ) -> Optional[MemoryObj]:
        """
        Allocate memory object with memory allocator.
        Use LRU evictor if eviction is enabled.
        """
        # TODO (Jiayi): We might need to pre-allocate and management
        # disk in a similar way as CPU.
        return self.allocator_backend.allocate(
            shape, dtype, fmt, eviction=eviction, busy_loop=busy_loop
        )

    @_lmcache_nvtx_annotate
    def batched_allocate(
        self,
        shape: torch.Size,
        dtype: torch.dtype,
        batch_size: int,
        fmt: MemoryFormat = MemoryFormat.KV_2LTD,
        eviction=True,
        busy_loop=True,
    ) -> Optional[MemoryObj]:
        """
        Batched allocate memory object with memory allocator.
        Use LRU evictor if eviction is enabled.
        """
        # TODO (Jiayi): We might need to pre-allocate and management
        # disk in a similar way as CPU.
        return self.allocator_backend.batched_allocate(
            shape, dtype, batch_size, fmt, eviction=eviction, busy_loop=busy_loop
        )

    def put(
        self,
        key: CacheEngineKey,
        memory_obj: MemoryObj,
        location: Optional[str] = None,
    ) -> None:
        """
        Non-blocking function to put the memory object into the storages.
        Do not store if the same object is being stored (handled here by
        storage manager) or has been stored (handled by storage backend).
        """
        raise RuntimeError(
            "StorageManager.put is deprecated and should not be called anymore"
        )
        for backend_name, backend in self.storage_backends.items():
            if location and backend_name != location:
                continue
            backend.submit_put_task(key, memory_obj)

        memory_obj.ref_count_down()

    # TODO(Jiayi): location and transfer_spec might be redundant
    def batched_put(
        self,
        keys: Sequence[CacheEngineKey],
        memory_objs: List[MemoryObj],
        transfer_spec=None,  # TODO(Jiayi): add type check
        location: Optional[str] = None,
    ) -> None:
        """
        Non-blocking function to batched put the memory objects into the
        storage backends.
        Do not store if the same object is being stored (handled here by
        storage manager) or has been stored (handled by storage backend).
        """

        if self.enable_nixl or (location and location == "NixlBackend"):
            self.allocator_backend.batched_submit_put_task(
                keys, memory_objs, transfer_spec=transfer_spec
            )

            cpu_memory_objs = []
            cpu_keys = []
            if len(self.storage_backends) > 1:
                # TODO(Jiayi): Optimize this with batched_allocate
                # TODO(Jiayi): Refactor this into gpu connector.
                for key, memory_obj in zip(keys, memory_objs, strict=False):
                    if self.local_cpu_backend.contains(key):
                        continue
                    assert isinstance(self.local_cpu_backend, LocalCPUBackend)
                    cpu_memory_obj = self.local_cpu_backend.allocate(
                        shape=memory_obj.get_shape(),
                        dtype=memory_obj.get_dtype(),
                        fmt=memory_obj.meta.fmt,
                        eviction=True,
                        busy_loop=False,
                    )
                    if cpu_memory_obj is None:
                        break
                    with torch.cuda.stream(self.nixl_offload_stream):
                        cpu_memory_obj.tensor.copy_(
                            memory_obj.tensor, non_blocking=True
                        )
                    cpu_memory_objs.append(cpu_memory_obj)
                    cpu_keys.append(key)
                self.nixl_offload_stream.synchronize()

                for memory_obj in memory_objs:
                    memory_obj.ref_count_down()
                memory_objs = cpu_memory_objs
                keys = cpu_keys

        for backend_name, backend in self.storage_backends.items():
            if backend_name == "NixlBackend":
                continue
            if location and backend_name != location:
                continue
            # NOTE: the handling of exists_in_put_tasks
            # is done in the backend
            backend.batched_submit_put_task(keys, memory_objs)

        if self.lookup_server is not None:
            self.lookup_server.batched_insert(keys)

        for memory_obj in memory_objs:
            memory_obj.ref_count_down()

    def get(
        self,
        key: CacheEngineKey,
        location: Optional[str] = None,
    ) -> Optional[MemoryObj]:
        """
        Blocking function to get the memory object from the storages.
        """

        # Search all backends for blocking get
        for backend_name, backend in self.storage_backends.items():
            if location and backend_name != location:
                continue
            # TODO(Jiayi): need to make sure all memory_objs returned
            # are allocated by the allocator backend.
            memory_obj = backend.get_blocking(key)
            if memory_obj:
                if backend_name not in ["LocalCPUBackend", "NixlBackend"]:
                    local_cpu_backend = self.storage_backends["LocalCPUBackend"]
                    assert isinstance(local_cpu_backend, LocalCPUBackend)
                    local_cpu_backend.submit_put_task(key, memory_obj)
                return memory_obj

        return None

    def batched_get(
        self,
        keys: List[CacheEngineKey],
        location: Optional[str] = None,
    ) -> Optional[List[Optional[MemoryObj]]]:
        """
        Blocking function to get the memory objects from the storages.
        """
        # TODO (ApostaC): remove the nested optional here
        for backend_name, storage_backend in self.storage_backends.items():
            if location and backend_name != location:
                continue
            memory_objs = storage_backend.batched_get_blocking(keys)
            if memory_objs:
                return memory_objs
        return None

    def layerwise_batched_get(
        self,
        keys: List[List[CacheEngineKey]],
        location: Optional[str] = None,
    ) -> Generator[Future, None, None]:
        """
        Non-blocking function to get the memory objects into the storages
        in a layerwise manner.
        Do not store if the same object is being stored (handled here by
        storage manager) or has been stored (handled by storage backend).

        :param List[List[CacheEngineKey]] keys: The keys to get. The first
            dimension corresponds to the number of layers, and the second
            dimension corresponds to the number of chunks.

        :return: A generator that yields a future for each layer.
        """
        if location is None:
            location = "LocalCPUBackend"

        for keys_multi_chunk in keys:
            # Retrieve all chunks for one layer
            backend = self.storage_backends[location]
            # TODO(Jiayi): need to make async loading and layerwise compatible
            task = asyncio.run_coroutine_threadsafe(
                backend.batched_get_non_blocking("fake_lookup_id", keys_multi_chunk),
                self.loop,
            )
            yield task

    def prefetch_single_done_callback(
        self,
        future: asyncio.Future,
        keys: list[CacheEngineKey],
        backend_name: str,
    ) -> None:
        """
        Callback function when a single prefetch task
        (i.e., prefetching from a single backend) is done.
        """
        # TODO(Jiayi): support write-back policy here
        pass

    def prefetch_all_done_callback(
        self,
        task: asyncio.Future,
        lookup_id: str,
        retrieved_length: int,
    ) -> None:
        """
        Callback function when all prefetch tasks
        (i.e., prefetching from all backends for the entire request) are done.
        """
        assert self.async_lookup_server is not None
        self.event_manager.update_event_status(
            EventType.LOADING, lookup_id, status=EventStatus.DONE
        )
        self.async_lookup_server.send_response_to_scheduler(lookup_id, retrieved_length)

    async def async_lookup_and_prefetch(
        self,
        lookup_id: str,
        keys: list[CacheEngineKey],
        cum_chunk_lengths: list[int],
        search_range: Optional[list[str]] = None,
        pin: bool = False,
    ) -> None:
        """
        Perform asynchronous lookup and prefetching across all storage backends.

        :param str lookup_id: The unique id (e.g., request id) for the request.
        :param list[CacheEngineKey] keys: The keys to lookup and prefetch.
        :param list[int] cum_chunk_lengths: The cumulative lengths of the chunks.
        :param Optional[list[str]] search_range: The range of storage backends
        to search in. Should be a subset of ["LocalCPUBackend",
        "LocalDiskBackend"] for now. If None, search in all backends.
        :param bool pin: Whether to pin the keys.
        """

        # NOTE(Jiayi): Currently, the retrieval pattern is always
        # prefix-based. That is, we retrieve 0-t1 tokens from backend 1
        # and retrieve t1-t2 tokens from backend 2, etc. The assumption
        # here is that the suffix chunks are more likely to be evicted
        # than the prefix chunks.
        # TODO(Jiayi): We need to change/optimize this for non-prefix
        # based retrieval patterns or cases where middle chunks are missing.

        num_total_chunks = len(keys)
        num_total_hit_chunks = 0
        loading_tasks = []
        for backend_name, backend in self.storage_backends.items():
            if search_range and backend_name not in search_range:
                continue
            num_hit_chunks = await backend.batched_async_contains(lookup_id, keys, pin)

            if num_hit_chunks == 0:
                continue

            num_total_hit_chunks += num_hit_chunks

            loading_task = asyncio.create_task(
                backend.batched_get_non_blocking(lookup_id, keys[:num_hit_chunks])
            )
            loading_task.add_done_callback(
                functools.partial(
                    self.prefetch_single_done_callback,
                    keys=keys,
                    backend_name=backend_name,
                )
            )

            loading_tasks.append(loading_task)

            if num_total_hit_chunks == num_total_chunks:
                break
            keys = keys[num_hit_chunks:]

        # If no chunks were hit across all backends, respond immediately and return.
        if num_total_hit_chunks == 0:
            if self.async_lookup_server is not None:
                self.async_lookup_server.send_response_to_scheduler(lookup_id, 0)
            return

        all_done = asyncio.gather(*loading_tasks)
        # Register the event before adding the callback to avoid race conditions
        self.event_manager.add_event(
            EventType.LOADING,
            lookup_id,
            all_done,
        )
        all_done.add_done_callback(
            lambda future: self.prefetch_all_done_callback(
                future, lookup_id, cum_chunk_lengths[num_total_hit_chunks]
            )
        )

    def contains(
        self,
        key: CacheEngineKey,
        search_range: Optional[List[str]] = None,
        pin: bool = False,
    ) -> Optional[str]:
        """
        Check whether the key exists in the storage backend.

        :param CacheEngineKey key: The key to check.

        :param Optional[List[str]] search_range: The range of storage backends
        to search in. Should be a subset of ["LocalCPUBackend",
        "LocalDiskBackend"] for now.
        If None, search in all backends.

        :param bool pin: Whether to pin the key.

        return: True if the key exists in the specified storage backends.
        """

        for backend_name, backend in self.storage_backends.items():
            if search_range and backend_name not in search_range:
                continue

            # NOTE(Jiayi): We do not pin for NixlBackend
            if backend_name == "NixlBackend":
                pin = False

            if backend.contains(key, pin):
                return backend_name

        return None

    def touch_cache(self):
        for backend_name, backend in self.storage_backends.items():
            if backend_name == "LocalCPUBackend" or backend_name == "LocalDiskBackend":
                backend.touch_cache()

    def remove(
        self,
        key: CacheEngineKey,
        locations: Optional[List[str]] = None,
    ) -> int:
        """
        Remove the key and the corresponding cache in the specified
        locations.

        :param CacheEngineKey key: The key to remove.

        :param Optional[List[str]] locations: The range of storage backends
        to perform `remove` in.
        Should be a subset of ["LocalCPUBackend", "LocalDiskBackend"] for now.
        If None, perform `remove` in all backends.

        return: Total number of removed caches in the specified
        storage backends.
        """

        num_removed = 0
        for backend_name, backend in self.storage_backends.items():
            # TODO(Jiayi): need to handle remove in non-cpu backends
            if locations is None or backend_name in locations:
                num_removed += backend.remove(key)

        return num_removed

    def batched_remove(
        self,
        keys: List[CacheEngineKey],
        locations: Optional[List[str]] = None,
    ) -> int:
        """
        Batched remove the keys and the corresponding cache in the specified
        locations.

        :param List[CacheEngineKey] keys: The keys to remove.

        :param Optional[List[str]] locations: The range of storage backends
        to perform `remove` in.
        Should be a subset of ["LocalCPUBackend", "LocalDiskBackend"] for now.
        If None, perform `remove` in all backends.

        return: Total number of removed caches in the specified
        storage backends.
        """
        num_removed = 0
        for backend_name, backend in self.storage_backends.items():
            if locations is None or backend_name in locations:
                num_removed += backend.batched_remove(keys)

        return num_removed

    def batched_unpin(
        self,
        keys: List[CacheEngineKey],
        locations: Optional[List[str]] = None,
    ) -> None:
        """
        Unpin the keys in the specified locations.

        :param List[CacheEngineKey] keys: The keys to unpin.

        :param Optional[List[str]] locations: The range of storage backends
        to perform `unpin` in.
        Should be a subset of ["LocalCPUBackend", "LocalDiskBackend"] for now.
        If None, perform `unpin` in all backends.
        """
        for backend_name, backend in self.storage_backends.items():
            if locations is None or backend_name in locations:
                for key in keys:
                    backend.unpin(key)

    def clear(
        self,
        locations: Optional[List[str]] = None,
    ) -> int:
        """
        Clear all caches in the specified locations.

        :param Optional[List[str]] locations: The range of storage backends
        to perform `clear` in.
        Should be a subset of ["LocalCPUBackend", "LocalDiskBackend"] for now.
        If None, perform `clear` in all backends.

        return: Total number of cleared tokens in the specified
        storage backends.
        """

        num_cleared_tokens = 0
        for backend_name, backend in self.storage_backends.items():
            # TODO(Jiayi): need to handle remove in non-cpu backends
            if locations is None or backend_name in locations:
                if hasattr(backend, "clear"):
                    num_cleared_tokens += backend.clear()
                else:
                    logger.warning(
                        f"Storage backend {backend_name} does not support "
                        "clear operation. Skipping."
                    )

        return num_cleared_tokens

    def close(self):
        for backend in self.storage_backends.values():
            backend.close()

        # using threadsafe method here as stop modifies
        # the internal state of the loop (in another thread)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread.is_alive():
            self.thread.join()

        logger.info("Storage manager closed.")
