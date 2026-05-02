import time

# Simple in-memory cache: stores {query: (value, expire_time)}
_cache = {}
TTL = 300  # Cache duration in seconds

def get_from_cache(query):
    """Retrieve results from cache (if it exists and hasn't expired)"""
    record = _cache.get(query)
    if record:
        value, expire = record
        if time.time() < expire:
            return value
        else:
            # Cache expired, remove the record
            del _cache[query]
    return None

def save_to_cache(query, results):
    """Save results to cache"""
    _cache[query] = (results, time.time() + TTL)
