"""
Tests for the caching system.

This module tests the cache functionality including storage,
retrieval, and expiration mechanisms.
"""

import time
from app.cache import save_to_cache, get_from_cache, _cache


def test_cache_store_and_retrieve():
    """
    Test basic cache storage and retrieval functionality.

    Verifies that data can be saved to the cache and successfully
    retrieved using the same key.
    """
    # Store a list in the cache with key "q1"
    save_to_cache("q1", [1, 2, 3])
    assert get_from_cache("q1") == [1, 2, 3]  # Verify the data matches what was stored


def test_cache_expiry():
    """
    Test cache expiration mechanism.

    Verifies that cached data expires after the TTL (Time To Live)
    period and returns None when attempting to retrieve expired data.
    """
    # Store data in the cache with key "q2"
    save_to_cache("q2", "data")

    # by manually manipulating the cache's internal structure
    _cache["q2"] = ("data", time.time() - 1)

    # Verify that expired data returns None (not the original "data")
    # The get_from_cache function should detect expiration and delete the entry
    assert get_from_cache("q2") is None
