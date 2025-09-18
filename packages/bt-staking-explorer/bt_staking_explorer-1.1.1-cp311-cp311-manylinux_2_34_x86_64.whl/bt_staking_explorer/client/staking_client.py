"""
StakingClient - Main client for BT Staking Explorer
"""

from itertools import islice
from typing import Any, Callable, Generator, Iterable, TypeVar
from substrateinterface import SubstrateInterface
from substrateinterface.storage import StorageKey


class StakingClient:
    """Client for interacting with BT Staking Explorer"""

    _substrate: SubstrateInterface | None = None

    def __init__(
        self, url_or_client: str | SubstrateInterface, logger: Callable | None = None
    ):
        """
        Initialize StakingClient

        Args:
            url_or_client: Substrate node URL or SubstrateInterface instance
            logger: Optional logger function (defaults to print)
        """
        if isinstance(url_or_client, str):
            self.url = url_or_client
            self._substrate = None
        else:
            self.url = url_or_client.url
            self._substrate = url_or_client

        self.logger = logger or print

    @property
    def substrate(self) -> SubstrateInterface:
        """Get or create SubstrateInterface instance"""
        if self._substrate is None:
            self._substrate = SubstrateInterface(url=self.url)
        return self._substrate

    def get_hotkey_stakes(self, requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Get basic stakes for hotkeys using Rust module

        Args:
            requests: List of requests with hotkey, netuid, block_hash (optional)

        Returns:
            List of results with stakes
        """
        try:
            from bt_staking_explorer import get_hotkey_stakes

            return get_hotkey_stakes(self.url, requests)
        except ImportError:
            raise ImportError(
                "bt_staking_explorer Rust module not available. Please build it first."
            )

    def _get_all_hotkey_stakes_for_netuid(
        self, netuid: int, block_hash: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all hotkey stakes for a specific netuid using Rust module

        Args:
            netuid: Network UID
            block_hash: Optional block hash to query specific state

        Returns:
            List of stakes for all hotkeys in the specified netuid
        """
        try:
            from bt_staking_explorer import get_all_hotkeys_stakes_for_netuid

            return get_all_hotkeys_stakes_for_netuid(self.url, netuid, block_hash)
        except ImportError:
            raise ImportError(
                "bt_staking_explorer Rust module not available. Please build it first."
            )

    def get_all_hotkey_stakes_for_netuid(
        self, netuid: int, block_hash: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all hotkey stakes for a specific netuid

        Args:
            netuid: Network UID
            block_hash: Optional block hash to query specific state

        Returns:
            List of stakes for all hotkeys in the specified netuid
        """
        stakes_with_errors = self._get_all_hotkey_stakes_for_netuid(netuid, block_hash)
        valid_stakes = []
        for record in stakes_with_errors:
            if "error" in record:
                self.logger(
                    f"Error fetching stakes for hotkey {record.get('hotkey', 'unknown')} and hash {record.get('block_hash', 'None')}: {record['error']}"
                )
                continue
            valid_stakes.append(record)

        if len(valid_stakes) != len(stakes_with_errors):
            self.logger(
                f"Encountered {len(stakes_with_errors) - len(valid_stakes)} errors while fetching stakes"
            )

        return valid_stakes

    def get_all_hotkeys(self, netuid: int, block_hash: str | None = None) -> list[str]:
        """
        Get all hotkeys for a specific netuid

        Args:
            netuid: Network UID

        Returns:
            List of hotkeys for the specified netuid
        """
        try:
            from bt_staking_explorer import get_all_hotkeys

            return get_all_hotkeys(self.url, netuid, block_hash)
        except ImportError:
            raise ImportError(
                "bt_staking_explorer Rust module not available. Please build it first."
            )

    def get_hotkey_stakes_with_parents(
        self, requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Get stakes with parent information - optimized version

        Args:
            requests: List of requests with hotkey, netuid, block_hash (optional)

        Returns:
            List of results with stakes and parents
        """
        # 1. Get all parents for all hotkeys first
        self.logger("Getting parents for all hotkeys...")
        parent_mapping = self._get_all_parents(requests)

        # 2. Create requests for all hotkeys (children + parents)
        all_requests = self._create_all_requests(requests, parent_mapping)

        # 3. Get stakes for all hotkeys in one batch
        self.logger(f"Getting stakes for {len(all_requests)} hotkeys...")
        all_stakes_results = self.get_hotkey_stakes(all_requests)

        # 4. Process results and handle errors
        return self._process_results_with_errors(
            requests, all_stakes_results, parent_mapping
        )

    def _get_all_parents(
        self, requests: list[dict[str, Any]]
    ) -> dict[tuple, list[dict[str, Any]]]:
        """
        Get parents for all hotkeys in one batch

        Args:
            requests: List of requests

        Returns:
            Mapping of (child hotkey, netuid, block_hash) -> list of parents

        """
        T = TypeVar("T")

        def chunked(iterable: Iterable[T], size: int) -> Generator[list[T], None, None]:
            """
            Splits an iterable into chunks of a specified size.

            Args:
                iterable (Iterable[T]): The input iterable to be chunked.
                size (int): The size of each chunk.

            Yields:
                Generator[list[T], None, None]: A generator yielding chunks as lists.
            """
            it = iter(iterable)
            while chunk := list(islice(it, size)):
                yield chunk

        parent_mapping = {}

        # Group requests by block_hash only (can batch different netuids with same block_hash)
        requests_by_block_hash = {}
        for request in requests:
            hotkey = request["hotkey"]
            netuid = request["netuid"]
            block_hash = request.get("block_hash")

            if block_hash not in requests_by_block_hash:
                requests_by_block_hash[block_hash] = []
            requests_by_block_hash[block_hash].append((hotkey, netuid))

        # Process each block_hash group with batch queries
        for block_hash, hotkey_netuid_pairs in requests_by_block_hash.items():
            try:
                self.substrate.init_runtime(block_hash)
                # Create all storage keys for this block_hash
                keys = []
                for hotkey, netuid in hotkey_netuid_pairs:
                    key = StorageKey.create_from_storage_function(
                        "SubtensorModule",
                        "ParentKeys",
                        [hotkey, netuid],
                        runtime_config=self.substrate.runtime_config,
                        metadata=self.substrate.metadata,
                    )
                    keys.append(key)

                values = []
                for chunk in chunked(keys, 64):
                    values.extend(
                        [
                            scale_value.value
                            for _, scale_value in self.substrate.query_multi(
                                chunk, block_hash
                            )
                        ]
                    )

                for (hotkey, netuid), value in zip(hotkey_netuid_pairs, values):
                    parents = []

                    if value:
                        # value contains Vec<(proportion, parent)>
                        for parent_data in value:
                            if len(parent_data) == 2:
                                proportion, parent_hotkey = parent_data
                                parent_info = {
                                    "hotkey": parent_hotkey,
                                    "proportion": proportion,
                                }
                                parents.append(parent_info)

                    parent_mapping[(hotkey, netuid, block_hash)] = parents
                    self.logger(
                        f"Found {len(parents)} parents for {hotkey} at block_hash {block_hash}"
                    )

            except Exception as e:
                self.logger(f"Error getting parents for block_hash {block_hash}: {e}")
                raise

        return parent_mapping

    def _create_all_requests(
        self,
        original_requests: list[dict[str, Any]],
        parent_mapping: dict[tuple, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """
        Create requests for all hotkeys (children + parents)

        Args:
            original_requests: Original requests
            parent_mapping: Mapping of (hotkey, netuid, block_hash) -> parents

        Returns:
            List of all requests including parents
        """
        all_requests = []
        processed_hotkeys = set()

        # Add original requests
        for request in original_requests:
            hotkey = request["hotkey"]
            netuid = request["netuid"]
            block_hash = request.get("block_hash")

            if (hotkey, netuid, block_hash) not in processed_hotkeys:
                all_requests.append(
                    {
                        "hotkey": hotkey,
                        "netuid": netuid,
                        **({"block_hash": block_hash} if block_hash else {}),
                    }
                )
                processed_hotkeys.add((hotkey, netuid, block_hash))

        # Add parent requests
        for (_, child_netuid, block_hash_from_map), parents in parent_mapping.items():
            for parent in parents:
                parent_hotkey = parent["hotkey"]
                parent_netuid = parent.get(
                    "netuid", child_netuid
                )  # Assume same netuid if not specified

                if (
                    parent_hotkey,
                    parent_netuid,
                    block_hash_from_map,
                ) not in processed_hotkeys:
                    all_requests.append(
                        {
                            "hotkey": parent_hotkey,
                            "netuid": parent_netuid,
                            **(
                                {"block_hash": block_hash_from_map}
                                if block_hash_from_map
                                else {}
                            ),
                        }
                    )
                    processed_hotkeys.add(
                        (parent_hotkey, parent_netuid, block_hash_from_map)
                    )

        return all_requests

    def _process_results_with_errors(
        self,
        original_requests: list[dict[str, Any]],
        all_stakes_results: list[dict[str, Any]],
        parent_mapping: dict[tuple, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """
        Process results and handle errors

        Args:
            original_requests: Original requests
            all_stakes_results: Results from get_hotkey_stakes
            parent_mapping: Mapping of (hotkey, netuid, block_hash) -> parents

        Returns:
            Processed results with error handling
        """
        # Create lookup dictionary for stakes by hotkey
        filtered_stakes_map = {}
        error_count = 0

        for result in all_stakes_results:
            if "error" in result:
                self.logger(
                    f"Error for hotkey {result.get('hotkey', 'unknown')}: {result['error']}"
                )
                error_count += 1
                continue

            key = (result["hotkey"], result["netuid"], result.get("block_hash"))
            filtered_stakes_map[key] = result["stakes"]

        if error_count > 0:
            self.logger(f"Encountered {error_count} errors during stake retrieval")

        # Build final results
        final_results = []
        for request in original_requests:
            hotkey = request["hotkey"]
            netuid = request["netuid"]
            block_hash = request.get("block_hash")

            key = (hotkey, netuid, block_hash)

            # Get child stakes
            child_stakes = filtered_stakes_map.get(key, [])
            if not child_stakes:
                self.logger(f"No stakes found for child hotkey {key}")
                continue

            # Get parents for this hotkey
            parents = parent_mapping.get(key, [])

            # Create ParentInfo objects with their stakes
            parent_infos = []
            for parent in parents:
                parent_hotkey = parent["hotkey"]
                key = (parent_hotkey, netuid, block_hash)
                parent_stakes = filtered_stakes_map.get(key, [])

                if not parent_stakes:
                    self.logger(f"No stakes found for parent key: {key}")
                    continue

                parent_info = {
                    "hotkey": parent_hotkey,
                    "proportion": parent["proportion"],
                    "stakes": parent_stakes,
                }
                parent_infos.append(parent_info)

            # Create final result with parents at hotkey level
            final_result = {
                "hotkey": hotkey,
                "netuid": netuid,
                "block_hash": block_hash,
                "stakes": child_stakes,  # Original stakes without parents
                "parents": parent_infos,  # Parents at hotkey level
            }
            final_results.append(final_result)

        return final_results

    def _get_parents_for_hotkey(
        self, hotkey: str, netuid: int, block_hash: str | None
    ) -> list[dict[str, Any]]:
        """Get parents for a hotkey"""
        try:
            result = self.substrate.query(
                module="SubtensorModule",
                storage_function="ParentKeys",
                params=[hotkey, netuid],
                block_hash=block_hash,
            )

            parents = []

            if result and result.value:
                # result.value contains Vec<(proportion, parent)>
                for parent_data in result.value:
                    if len(parent_data) == 2:
                        proportion, parent_hotkey = parent_data

                        parent_info = {
                            "hotkey": parent_hotkey,
                            "proportion": proportion,
                        }
                        parents.append(parent_info)

            return parents

        except Exception as e:
            self.logger(f"Error getting parents for {hotkey}: {e}")
            return []
