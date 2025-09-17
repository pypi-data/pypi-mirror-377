import copy
import os

import numpy as np
import torch
import torch.multiprocessing as mp
from torch.utils.data import IterableDataset

from recis.io.map_dataset import MapDataset
from recis.io.state_dataset import StateDataset
from recis.io.wrap_end_dataset import WrapEndDataset
from recis.nn.functional.ragged_ops import ragged_to_sparse
from recis.ragged.tensor import RaggedTensor
from recis.utils.logger import Logger


if not os.environ.get("BUILD_DOCUMENT", None) == "1":
    from column_io.dataset import dataset as dataset_io

logger = Logger(__name__)


def is_string_dtype(arr):
    """Checks if a numpy array has string data type.

    Args:
        arr (np.ndarray): Input numpy array to check.

    Returns:
        bool: True if the array has string data type (Unicode, byte string, or object), False otherwise.
    """
    return arr.dtype.kind in {"U", "S", "O"}


def _batch_convert(dense_column, ragged_format, dtype):
    """Creates a batch conversion function for processing raw data into PyTorch tensors.

    This function returns a wrapper that converts raw batch data from the column IO
    system into appropriate PyTorch tensor formats, handling both dense and ragged
    (variable-length) data structures.

    Args:
        dense_column (List[str]): List of column names that should be treated as dense tensors.
        ragged_format (bool): Whether to use RaggedTensor format for variable-length data.
        dtype (torch.dtype): Target data type for floating-point tensors.

    Returns:
        callable: A wrapper function that processes raw batch data.

    Example:
        >>> converter = _batch_convert(["age", "score"], True, torch.float32)
        >>> processed_batch = converter(raw_input_data)
    """

    def _wrapper_(input_data):
        batch_list = []
        for table, raw_batch in enumerate(input_data):
            batch_list.append({})
            for fn, data in raw_batch.items():
                if isinstance(data[0][0], np.ndarray) and is_string_dtype(data[0][0]):
                    if data[0][0].dtype.kind == "O":
                        try:
                            data[0][0] = data[0][0].astype("S")
                        except Exception:
                            data[0][0] = data[0][0].astype("U")
                    batch_list[table][fn] = data[0]
                elif fn in dense_column or fn == "_indicator":
                    values = torch.from_dlpack(data[0][0])
                    if torch.is_floating_point(values):
                        values = values.to(dtype)
                    batch_list[table][fn] = values
                else:
                    if len(data) == 1:
                        data = data[0]
                        values = torch.from_dlpack(data[0])
                        if torch.is_floating_point(values):
                            values = values.to(dtype)
                        row_splits = [torch.from_dlpack(d) for d in data[1:][::-1]]
                        dense_shape = tuple(
                            [row_splits[0].numel() - 1] + [-1] * len(row_splits)
                        )
                        if ragged_format:
                            batch_list[table][fn] = RaggedTensor(
                                values=values,
                                offsets=row_splits,
                                dense_shape=dense_shape,
                            )
                        elif len(row_splits) > 0:
                            batch_list[table][fn] = ragged_to_sparse(values, row_splits)
                        else:
                            batch_list[table][fn] = values
                    else:
                        value_data = data[0]
                        values = torch.from_dlpack(value_data[0])
                        if torch.is_floating_point(values):
                            values = values.to(dtype)
                        row_splits = [
                            torch.from_dlpack(d) for d in value_data[1:][::-1]
                        ]
                        dense_shape = tuple(
                            [row_splits[0].numel() - 1] + [-1] * len(row_splits)
                        )

                        weight_data = data[1]
                        w_values = torch.from_dlpack(weight_data[0])
                        if torch.is_floating_point(w_values):
                            w_values = w_values.to(dtype)
                        # w_row_splits = [torch.from_dlpack(d) for d in weight_data[1:][::-1]]
                        if ragged_format:
                            batch_list[table][fn] = RaggedTensor(
                                values=values,
                                offsets=row_splits,
                                weight=w_values,
                                dense_shape=dense_shape,
                            )
                        else:
                            batch_list[table][fn] = ragged_to_sparse(values, row_splits)
                            batch_list[table][fn + "_weight"] = ragged_to_sparse(
                                values, row_splits
                            )
        return batch_list

    return _wrapper_


class DatasetBase(IterableDataset):
    """Base class for all RecIS dataset implementations.

    This class provides the foundational functionality for data loading and preprocessing
    in RecIS. It inherits from PyTorch's IterableDataset and implements common features
    such as multi-threading, batching, prefetching, and data transformation pipelines.

    The DatasetBase class supports:
    - Distributed data loading across multiple workers
    - Parallel data reading with configurable thread counts
    - Automatic batching with optional remainder dropping
    - Data prefetching for improved performance
    - Flexible data transformation pipelines
    - State management for resumable training
    - Both dense and ragged tensor formats

    Args:
        batch_size (int): Number of samples per batch.
        worker_idx (int): Index of current worker in distributed setup. Defaults to 0.
        worker_num (int): Total number of workers in distributed setup. Defaults to 1.
        read_threads_num (int): Number of parallel reading threads. Defaults to 4.
        pack_threads_num (int, optional): Number of packing threads. Defaults to None.
        prefetch (int): Number of batches to prefetch. Defaults to 1.
        is_compressed (bool): Whether data is compressed. Defaults to False.
        drop_remainder (bool): Whether to drop the last incomplete batch. Defaults to False.
        worker_slice_batch_num (int, optional): Number of batches per worker slice. Defaults to None.
        ragged_format (bool): Whether to use RaggedTensor format for variable-length data. Defaults to True.
        transform_fn (callable or List[callable], optional): Data transformation function(s). Defaults to None.
        save_interval (int): Interval for saving IO state. Defaults to 100.
        dtype (torch.dtype): Data type for floating-point tensors. Defaults to torch.float32.
        device (str): Target device for data placement ("cpu", "cuda", or "pin"). Defaults to "cpu".

    Example:
        >>> # Create a custom dataset by inheriting from DatasetBase
        >>> class MyDataset(DatasetBase):
        ...     def make_dataset_fn(self):
        ...         # Implement dataset creation logic
        ...         pass
        ...
        ...     def _shard_path(self, sub_id, sub_num):
        ...         # Implement path sharding logic
        ...         pass
        >>> # Use the dataset
        >>> dataset = MyDataset(
        ...     batch_size=1024, read_threads_num=4, prefetch=2, device="cuda"
        ... )

    Note:
        This is an abstract base class. Subclasses must implement the `make_dataset_fn`
        and `_shard_path` methods to provide specific data source functionality.
    """

    def __init__(
        self,
        batch_size,
        worker_idx=0,
        worker_num=1,
        read_threads_num=4,
        pack_threads_num=None,
        prefetch=1,
        is_compressed=False,
        drop_remainder=False,
        worker_slice_batch_num=None,
        ragged_format=True,
        transform_fn=None,
        save_interval=100,
        dtype=torch.float32,
        device="cpu",
    ) -> None:
        super().__init__()
        self._dataset = None
        self._batch_size = batch_size
        self._worker_idx = worker_idx
        self._worker_num = worker_num
        self._read_threads_num = read_threads_num
        self._pack_threads_num = pack_threads_num
        self._prefetch = prefetch
        self._is_compressed = is_compressed
        self._drop_remainder = drop_remainder
        self._worker_slice_batch_num = worker_slice_batch_num
        self._dtype = dtype
        assert device in [
            "cpu",
            "cuda",
            "pin",
        ], f"Only support io result placed in `cpu|cuda|pin` but got {device}"
        self._device = device
        self._paths = []
        self._shard_paths = None
        self._select_column = []
        self._dense_column = []
        self._dense_default_value = []
        self._transform_fn = transform_fn
        if self._transform_fn is not None and not isinstance(
            self._transform_fn, (tuple, list)
        ):
            self._transform_fn = [self._transform_fn]
        self._ragged_format = ragged_format
        self._map_funcs = []
        self._filter_funcs = []

        self._save_interval = save_interval
        self._local_step = 0
        self._load_states = None
        self._shard_paths = None
        self._lock = mp.Lock()
        self._io_state = mp.Manager().dict()

    def varlen_feature(self, name):
        """Defines a variable-length feature column.

        Variable-length features are columns that contain sequences or lists of values
        with varying lengths across samples. These are typically processed as RaggedTensors
        or sparse tensors depending on the ragged_format setting.

        Args:
            name (str): Name of the feature column.

        Example:
            >>> dataset.varlen_feature("item_sequence")
            >>> dataset.varlen_feature("user_behavior_history")
        """
        if name not in self._select_column:
            self._select_column.append(name)

    def fixedlen_feature(self, name, default_value):
        """Defines a fixed-length feature column with default values.

        Fixed-length features are columns that have a consistent shape across all samples.
        Default values are used when the feature is missing or incomplete in the data.

        Args:
            name (str): Name of the feature column.
            default_value (List): Default value(s) to use when the feature is missing.
                Should be a list even for scalar values.

        Example:
            >>> dataset.fixedlen_feature("age", default_value=[25.0])
            >>> dataset.fixedlen_feature("gender", default_value=[0])
            >>> dataset.fixedlen_feature("embedding", default_value=[0.0] * 128)
        """
        if name not in self._select_column:
            self._select_column.append(name)
        if name not in self._dense_column:
            self._dense_column.append(name)
            self._dense_default_value.append(default_value)

    def map(self, map_func):
        """Adds a mapping function to the data processing pipeline.

        Mapping functions are applied to each batch after the initial data conversion.
        They can be used for custom data transformations, feature engineering, or
        data augmentation.

        Args:
            map_func (callable): Function that takes a batch dictionary and returns
                a modified batch dictionary.

        Example:
            >>> def normalize_features(batch):
            ...     batch["normalized_score"] = batch["score"] / 100.0
            ...     return batch
            >>> dataset.map(normalize_features)
        """
        self._map_funcs.append(map_func)

    def filter(self, filter_func):
        """Adds a filtering function to the data processing pipeline.

        Filtering functions are used to skip certain batches based on custom criteria.
        If a filter function returns True, the batch will be skipped.

        Args:
            filter_func (callable): Function that takes a batch dictionary and returns
                a boolean indicating whether to filter out (skip) the batch.

        Example:
            >>> def filter_empty_sequences(batch):
            ...     # Skip batches where all sequences are empty
            ...     return torch.all(batch["sequence_length"] == 0)
            >>> dataset.filter(filter_empty_sequences)
        """
        self._filter_funcs.append(filter_func)

    def make_dataset_fn(self):
        """Creates the dataset function for the specific data source.

        This is an abstract method that must be implemented by subclasses to define
        how to create a dataset from the data source (e.g., ORC files, ODPS tables).

        Returns:
            callable: A function that creates a dataset from input paths.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("make_dataset_fn not implemented")

    def _shard_path(self, sub_id, sub_num):
        """Shards data paths across multiple sub-processes.

        This is an abstract method that must be implemented by subclasses to define
        how to distribute data paths among different worker processes for parallel
        data loading.

        Args:
            sub_id (int): ID of the current sub-process.
            sub_num (int): Total number of sub-processes.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("_shard_path not implemented")

    def dump_io_state(self):
        """Dumps the current IO state for checkpointing.

        Returns the current state of the IO system, which can be used to resume
        data loading from a specific point during training recovery.

        Returns:
            Dict or None: Current IO state dictionary, or None if save_interval is 0.
        """
        if not self._save_interval:
            return None
        self._lock.acquire()
        cur_state = dict(self._io_state)
        self._lock.release()
        return cur_state

    def load_io_state(self, io_states):
        """Loads IO state for resuming data loading.

        Restores the IO system to a previously saved state, allowing training
        to resume from a specific data loading checkpoint.

        Args:
            io_states (Dict): Previously saved IO state dictionary.
        """
        if io_states:
            self._load_states = copy.deepcopy(io_states)

    def _create_state_dataset(self, dataset, sub_id, sub_num):
        """Creates a state-aware dataset wrapper for checkpointing.

        Wraps the dataset with state management capabilities to enable saving
        and loading of data loading progress for training recovery.

        Args:
            dataset: The base dataset to wrap.
            sub_id (int): ID of the current sub-process.
            sub_num (int): Total number of sub-processes.

        Returns:
            StateDataset: State-aware dataset wrapper.

        Raises:
            AssertionError: If loaded states don't match the expected sub-worker count.
        """
        assert self._load_states is None or len(self._load_states) == sub_num, (
            f"IO states size not equal to sub worker num, expect: {len(self._load_states)}, got: {sub_num}"
        )
        load_state = self._load_states[sub_id] if self._load_states else None
        dataset = StateDataset(
            dataset,
            self._lock,
            self._io_state,
            load_state=load_state,
            save_interval=self._save_interval,
            sub_id=sub_id,
        )
        return dataset

    def _get_sub_info(self):
        """Gets sub-process information for multi-worker data loading.

        Determines the current sub-process ID and total number of sub-processes
        based on PyTorch's DataLoader worker information.

        Returns:
            Tuple[int, int]: A tuple containing (sub_id, sub_num).
        """
        worker_info = torch.utils.data.get_worker_info()
        if worker_info:
            sub_id = worker_info.id
            sub_num = worker_info.num_workers
        else:  # main process
            sub_id = 0
            sub_num = 1
        return sub_id, sub_num

    def _build_dataset(self):
        """Builds the complete data processing pipeline.

        This method constructs the full dataset pipeline including:
        1. Path sharding for distributed loading
        2. Parallel data reading
        3. Batching and prefetching
        4. State management
        5. Data transformation pipeline

        The pipeline is optimized for high-throughput data loading with support
        for various data formats and processing requirements.
        """
        self._shard_paths = []
        sub_id, sub_num = self._get_sub_info()
        self._shard_path(sub_id, sub_num)

        self._dataset = dataset_io.Dataset.from_list_string(self._shard_paths)
        self._dataset = self._dataset.parallel(
            self.make_dataset_fn(),
            cycle_length=self._read_threads_num,
            block_length=1,
            sloppy=True,
            buffer_output_elements=1,
            prefetch_input_elements=0,
        )
        self._dataset = self._dataset.pack(
            self._batch_size,
            self._drop_remainder,
            parallel=self._pack_threads_num,
            pinned_result=(self._device == "pin"),
            gpu_result=(self._device == "cuda"),
        )
        if self._prefetch:
            self._dataset = self._dataset.prefetch(self._prefetch)
        self._dataset = self._create_state_dataset(self._dataset, sub_id, sub_num)
        map_funcs = [
            _batch_convert(self._dense_column, self._ragged_format, self._dtype)
        ]
        map_funcs.extend(self._map_funcs)
        if self._transform_fn:
            map_funcs.extend(self._transform_fn)
        self._dataset = MapDataset(self._dataset, map_funcs=map_funcs)
        self._dataset = WrapEndDataset(self._dataset)

    def __iter__(self):
        self._build_dataset()
        return iter(self._dataset)
