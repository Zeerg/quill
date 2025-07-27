# Response Caching

Quill includes a sophisticated multi-level caching system to improve fuzzing performance by avoiding redundant API calls.

## Overview

The caching system provides:
- **In-memory LRU cache** for instant access to recent responses
- **SQLite persistent cache** for long-term storage across runs
- **Automatic cache promotion** from disk to memory
- **TTL-based expiration** to ensure fresh results
- **Cache statistics** to monitor performance

## Performance Benefits

Caching can dramatically improve fuzzing performance:
- **100% faster** for repeated prompts
- **50-80% faster** for similar test runs
- **Reduced API costs** by avoiding duplicate requests
- **Offline capability** for cached responses

## Usage

### Basic Usage

Caching is enabled by default:

```bash
# Run with caching (default)
quill fuzz -c corpus.txt -o runs/test ollama --model llama2

# Disable caching
quill fuzz --no-cache -c corpus.txt -o runs/test ollama --model llama2

# Custom cache TTL (2 hours)
quill fuzz --cache-ttl 7200 -c corpus.txt -o runs/test ollama --model llama2
```

### Cache Location

Caches are stored in `.cache` directory adjacent to output directories:
```
runs/
├── test_run/
│   ├── prompt_0000.json
│   └── summary.json
└── .cache/
    └── response_cache.db
```

## Configuration Options

- `--no-cache`: Disable caching entirely
- `--cache-ttl SECONDS`: Set cache expiration time (default: 3600 = 1 hour)

## Cache Management

### View Cache Statistics

After a fuzzing run, check `summary.json` for cache performance:

```json
{
  "cache_stats": {
    "memory_hits": 245,
    "disk_hits": 89,
    "total_hits": 334,
    "misses": 166,
    "hit_rate": 0.668,
    "memory_entries": 500,
    "disk_entries": 1523
  }
}
```

### Export Cache Contents

Each run automatically exports cache contents to `cache_export.json`:

```json
{
  "exported_at": 1699123456.789,
  "entries": [
    {
      "prompt": "Tell me about Python",
      "response": "Python is a high-level programming language...",
      "model": "llama2",
      "temperature": 0.7,
      "timestamp": 1699123400.123,
      "hits": 5
    }
  ]
}
```

### Clear Cache

Remove cache files to start fresh:

```bash
# Clear specific run cache
rm -rf runs/.cache/

# Clear all caches
find runs -name ".cache" -type d -exec rm -rf {} +
```

## How It Works

### Cache Levels

1. **L1 Memory Cache**
   - Stores up to 1000 most recent responses
   - LRU eviction policy
   - Sub-millisecond access time

2. **L2 Disk Cache**
   - SQLite database for unlimited storage
   - Survives between runs
   - Indexed for fast lookups

### Cache Key Generation

Cache keys are generated from:
- Prompt text
- Model name
- Temperature setting

This ensures different models or temperatures get separate cache entries.

### Cache Flow

1. Check memory cache (fastest)
2. If miss, check disk cache
3. If disk hit, promote to memory
4. If miss, query model
5. Store successful response in both caches

## Best Practices

### When to Use Caching

✅ **Good for:**
- Development and testing
- Repeated runs with similar prompts
- Benchmarking mutation strategies
- Offline analysis of results

❌ **Not recommended for:**
- Production vulnerability assessments
- Testing model behavior changes
- Evaluating prompt variations

### Cache Optimization

1. **Adjust TTL based on use case**
   ```bash
   # Short TTL for rapidly changing models
   quill fuzz --cache-ttl 300 ...  # 5 minutes
   
   # Long TTL for stable models
   quill fuzz --cache-ttl 86400 ...  # 24 hours
   ```

2. **Pre-warm cache**
   ```bash
   # Run once to populate cache
   quill fuzz -c common_prompts.txt --max-prompts 1000 ...
   
   # Subsequent runs will be much faster
   quill fuzz -c test_prompts.txt ...
   ```

3. **Share cache between runs**
   ```bash
   # Use consistent output directory structure
   quill fuzz -o runs/model_test/v1 ...
   quill fuzz -o runs/model_test/v2 ...
   # Both will share runs/.cache/
   ```

## Advanced Features

### Cache-Only Mode

Run analysis on previously cached responses:

```python
from quill.core.cache import ResponseCache

# Load existing cache
cache = ResponseCache(Path("runs/.cache"))

# Export for analysis
cache.export_cache(Path("all_responses.json"))

# Get statistics
stats = cache.get_stats()
print(f"Total cached responses: {stats['disk_entries']}")
print(f"Cache hit rate: {stats['hit_rate']:.1%}")
```

### Custom Cache Implementation

Extend ResponseCache for custom behavior:

```python
class CustomCache(ResponseCache):
    def should_cache(self, response: str) -> bool:
        # Don't cache very short responses
        if len(response) < 50:
            return False
        return True
```

## Troubleshooting

### Cache Not Working

1. Check cache is enabled (no `--no-cache` flag)
2. Verify cache directory permissions
3. Ensure enough disk space
4. Check TTL hasn't expired

### High Miss Rate

1. Prompts may be too unique
2. Temperature variations creating different keys  
3. TTL too short for reuse
4. Different models being tested

### Cache Corruption

If cache becomes corrupted:
```bash
# Remove and recreate
rm -rf runs/.cache/
quill fuzz ...  # Will create fresh cache
```

## Performance Monitoring

Monitor cache effectiveness:

```bash
# Watch cache performance in real-time
watch -n 1 'grep -A5 "cache_stats" runs/latest/summary.json'
```

Cache statistics help optimize:
- **High hit rate (>50%)**: Cache is effective
- **Low hit rate (<20%)**: Consider disabling cache
- **Many evictions**: Increase memory cache size