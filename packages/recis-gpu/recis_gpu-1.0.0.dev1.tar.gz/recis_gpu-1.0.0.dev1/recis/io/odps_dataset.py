import column_io.dataset.dataset as column_io_dataset
import torch
from column_io.dataset.file_sharding import OdpsTableSharding


try:
    from column_io.dataset.odps_env_setup import (
        ensure_standard_path_format,
        init_odps_open_storage_session,
    )
except ImportError:

    def is_turn_on_odps_open_storage():
        """Fallback function when ODPS Open Storage is not available.

        Returns:
            bool: Always returns False when Open Storage is not available.
        """
        return False


from recis.io.dataset_base import DatasetBase
from recis.utils.logger import Logger


logger = Logger(__name__)

# Automatically select the appropriate ODPS dataset backend
if is_turn_on_odps_open_storage():
    odps_dataset_func = column_io_dataset.OdpsOpenStorageDataset
else:
    odps_dataset_func = column_io_dataset.OdpsTableColumnDataset
odps_dataset_func.load_plugin()


def get_table_size(table_name):
    """Get the size (number of rows) of an ODPS table.

    Args:
        table_name (str): The name of the ODPS table in format 'project.table'.

    Returns:
        int: The number of rows in the specified table.

    Example:
        ```python
        size = get_table_size("my_project.user_behavior_table")
        print(f"Table has {size} rows")
        ```
    """
    table_size = odps_dataset_func.get_table_size(table_name)
    return table_size


class OdpsDataset(DatasetBase):
    """ODPS Dataset for reading Open Data Processing Service tables.

    This class provides functionality to read ODPS tables efficiently with support for
    both sparse (variable-length) and dense (fixed-length) features. It extends
    DatasetBase to provide ODPS-specific optimizations including hash feature processing,
    table sharding, and batch processing.

    The OdpsDataset automatically detects and uses ODPS Open Storage when available,
    which provides better performance for large-scale data processing. It supports
    distributed training by allowing multiple workers to process different shards
    of the data concurrently.

    Attributes:
        hash_types (List[str]): List of hash algorithms used for features.
        hash_buckets (List[int]): List of hash bucket sizes for features.
        hash_features (List[str]): List of feature names that use hashing.

    Example:
        Creating and configuring an ODPS dataset:

        ```python
        # Initialize dataset
        dataset = OdpsDataset(
            batch_size=512, worker_idx=0, worker_num=4, shuffle=True, ragged_format=True
        )

        # Add ODPS tables
        dataset.add_paths(
            ["recommendation.user_features", "recommendation.item_features"]
        )

        # Configure sparse features with hashing
        dataset.varlen_feature(
            "user_clicked_items", hash_type="farm", hash_bucket=1000000
        )
        dataset.varlen_feature("item_categories", hash_type="murmur", hash_bucket=10000)

        # Configure dense features
        dataset.fixedlen_feature("user_age", default_value=25.0)
        dataset.fixedlen_feature("item_price", default_value=0.0)
        ```
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
        shuffle=False,
        ragged_format=True,
        transform_fn=None,
        save_interval=100,
        dtype=torch.float32,
        device="cpu",
    ) -> None:
        """Initialize OdpsDataset with configuration parameters.

        Args:
            batch_size (int): Number of samples per batch.
            worker_idx (int, optional): Index of current worker. Defaults to 0.
            worker_num (int, optional): Total number of workers. Defaults to 1.
            read_threads_num (int, optional): Number of reading threads. Defaults to 4.
            pack_threads_num (int, optional): Number of packing threads. Defaults to None.
            prefetch (int, optional): Number of batches to prefetch. Defaults to 1.
            is_compressed (bool, optional): Whether data is compressed. Defaults to False.
            drop_remainder (bool, optional): Whether to drop incomplete batches. Defaults to False.
            worker_slice_batch_num (int, optional): Number of batches per worker slice. Defaults to None.
            shuffle (bool, optional): Whether to shuffle the data. Defaults to False.
            ragged_format (bool, optional): Whether to use ragged tensor format. Defaults to True.
            transform_fn (callable, optional): Data transformation function. Defaults to None.
            save_interval (int, optional): Interval for saving checkpoints. Defaults to 100.
            dtype (torch.dtype, optional): Data type for tensors. Defaults to torch.float32.
            device (str, optional): Device for tensor operations. Defaults to "cpu".

        Note:
            The dataset automatically detects ODPS Open Storage availability and
            configures the appropriate backend for optimal performance.
        """
        super().__init__(
            batch_size,
            worker_idx,
            worker_num,
            read_threads_num,
            pack_threads_num,
            prefetch,
            is_compressed,
            drop_remainder,
            worker_slice_batch_num,
            ragged_format,
            transform_fn,
            save_interval,
            dtype,
            device,
        )
        self._shuffle = shuffle
        self._table_sizes = []
        self._total_row_count = 0
        self.hash_types = []
        self.hash_buckets = []
        self.hash_features = []

    def add_path(self, odps_table):
        """Add a single ODPS table to the dataset.

        Args:
            odps_table (str): ODPS table name in format 'project.table'.

        Example:
            ```python
            dataset.add_path("my_project.user_behavior_table")
            ```
        """
        self._paths.append(odps_table)
        self._table_sizes.append(0)

    def add_paths(self, odps_tables):
        """Add multiple ODPS tables to the dataset.

        Args:
            odps_tables (List[str]): List of ODPS table names in format 'project.table'.

        Example:
            ```python
            dataset.add_paths(
                [
                    "recommendation.user_features",
                    "recommendation.item_features",
                    "recommendation.interaction_logs",
                ]
            )
            ```
        """
        for table in odps_tables:
            self.add_path(table)

    def varlen_feature(self, name, hash_type=None, hash_bucket=0, trans_int8=False):
        """Configure a variable-length (sparse) feature with optional hashing.

        Variable-length features are columns that contain sequences or lists of values
        with varying lengths across samples. These features can optionally be processed
        with hash functions for dimensionality reduction and categorical encoding.

        Args:
            name (str): Name of the feature column in the ODPS tables.
            hash_type (str, optional): Hash algorithm to use for the feature.
                Supported values are "farm" (FarmHash) and "murmur" (MurmurHash).
                If None, no hashing is applied. Defaults to None.
            hash_bucket (int, optional): Size of the hash bucket (vocabulary size).
                Only used when hash_type is specified. Defaults to 0.
            trans_int8 (bool, optional): Whether to convert string data directly to
                int8 tensors without hashing. Only effective when hash_type is None.
                Defaults to False.

        Example:
            ```python
            # Sparse feature with FarmHash for large vocabularies
            dataset.varlen_feature(
                "user_clicked_items", hash_type="farm", hash_bucket=1000000
            )

            # Sparse feature with MurmurHash for smaller vocabularies
            dataset.varlen_feature(
                "item_categories", hash_type="murmur", hash_bucket=50000
            )

            # Raw sparse feature without hashing (for pre-processed IDs)
            dataset.varlen_feature("user_behavior_sequence")

            # String feature converted to int8 (for text processing)
            dataset.varlen_feature("review_tokens", trans_int8=True)
            ```

        Raises:
            AssertionError: If hash_type is not "farm" or "murmur" when specified.

        Note:
            Hash functions are useful for handling large categorical vocabularies
            by mapping them to a fixed-size space. FarmHash generally provides
            better distribution properties, while MurmurHash is faster for smaller
            vocabularies.
        """
        if name not in self._select_column:
            self._select_column.append(name)
            if hash_type:
                assert hash_type in [
                    "farm",
                    "murmur",
                ], "hash_type must be farm / murmur"
                self.hash_features.append(name)
                self.hash_buckets.append(hash_bucket)
                self.hash_types.append(hash_type)
            elif trans_int8:
                self.hash_features.append(name)
                self.hash_buckets.append(hash_bucket)
                self.hash_types.append("no_hash")

    def fixedlen_feature(self, name, default_value):
        """Configure a fixed-length (dense) feature.

        Fixed-length features are typically used for numerical data where each
        sample has exactly one value, such as user age, item price, or ratings.

        Args:
            name (str): Name of the feature column in the ODPS table.
            default_value (float): Default value to use when feature is missing.

        Example:
            ```python
            # Numerical features with default values
            dataset.fixedlen_feature("user_age", default_value=25.0)
            dataset.fixedlen_feature("item_price", default_value=0.0)
            dataset.fixedlen_feature("rating", default_value=3.0)
            ```

        Note:
            Default values are important for handling missing data gracefully
            and ensuring consistent tensor shapes across batches.
        """
        if name not in self._select_column:
            self._select_column.append(name)
        if name not in self._dense_column:
            self._dense_column.append(name)
            self._dense_default_value.append(default_value)

    def _shard_path(self, sub_id, sub_num):
        """Create table shards for distributed processing.

        This method partitions the input ODPS tables across multiple workers and threads
        to enable parallel data loading. It uses OdpsTableSharding to ensure
        balanced distribution of data and initializes ODPS Open Storage session
        when available.

        Args:
            sub_id (int): Sub-process identifier within the worker.
            sub_num (int): Total number of sub-processes per worker.

        Note:
            This is an internal method used by the dataset creation process.
            When ODPS Open Storage is available, it initializes the session
            with standardized paths and required columns for optimal performance.
        """
        if is_turn_on_odps_open_storage():
            standard_paths = ensure_standard_path_format(self._paths)
            init_odps_open_storage_session(
                standard_paths, required_data_columns=self._select_column
            )
        file_shard = OdpsTableSharding()
        file_shard.add_paths(self._paths)
        self._shard_paths = file_shard.partition(
            self._worker_idx * sub_num + sub_id,
            self._worker_num * sub_num,
            self._read_threads_num,
            slice_size=(
                self._worker_slice_batch_num * self._batch_size
                if self._worker_slice_batch_num
                else None
            ),
            shuffle=self._shuffle,
        )

    def make_dataset_fn(self):
        """Create a dataset factory function for ODPS table processing.

        This method returns a lambda function that creates a column_io Dataset
        from ODPS tables with the configured features and processing parameters.

        Returns:
            callable: A function that takes a table name and returns a Dataset object.

        Note:
            The returned function is used internally by the data loading pipeline
            to create dataset instances for each shard of data. It automatically
            uses the appropriate ODPS backend (Open Storage or traditional).
        """
        return lambda x: column_io_dataset.Dataset.from_odps_source(
            [x.decode() if isinstance(x, bytes) else x],
            self._is_compressed,
            self._batch_size,
            self._select_column,
            self.hash_features,
            self.hash_types,
            self.hash_buckets,
            self._dense_column,
            self._dense_default_value,
        )

    def get_table_size(self):
        """Calculate and return the sizes of all configured ODPS tables.

        This method iterates through all added ODPS tables and retrieves their sizes,
        updating the internal tracking of total row count for the dataset.
        When ODPS Open Storage is available, it initializes the session before
        querying table sizes.

        Returns:
            List[int]: List of table sizes (number of rows) corresponding to each table.

        Example:
            ```python
            dataset.add_paths(["project.table1", "project.table2"])
            sizes = dataset.get_table_size()
            print(f"Table sizes: {sizes}")
            ```

        Note:
            This method may take some time to execute as it queries the ODPS
            service for actual table statistics.
        """
        if is_turn_on_odps_open_storage():
            standard_paths = ensure_standard_path_format(self._paths)
            init_odps_open_storage_session(
                standard_paths, required_data_columns=self._select_column
            )
        for i, table_name in enumerate(self._paths):
            table_size = get_table_size(table_name)
            self._table_sizes[i] = table_size
            self._total_row_count += table_size
        return self._table_sizes
