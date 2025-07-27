# Async Fuzzing

Quill supports asynchronous request processing for significantly improved performance when fuzzing LLMs.

## Overview

The async mode processes multiple requests concurrently, reducing overall fuzzing time by:
- Batching requests for efficient processing
- Using connection pooling to reuse HTTP connections
- Processing multiple requests in parallel
- Eliminating wait time between sequential requests

## Performance Benefits

Typical performance improvements with async mode:
- **5-10x faster** for remote APIs (HTTP mode)
- **2-5x faster** for local models (Ollama mode)
- Scales linearly with batch size up to API rate limits

## Usage

### Basic Async Fuzzing

```bash
# Enable async mode with --async flag
quill fuzz --async -c corpus.txt -o runs/async_test --max-prompts 1000 \
    ollama --model llama2
```

### Advanced Configuration

```bash
# Customize batch size and concurrency
quill fuzz --async --batch-size 20 --max-concurrent 10 \
    -c corpus.txt -o runs/async_test --max-prompts 1000 \
    http --url https://api.example.com/v1/chat
```

### Configuration Options

- `--async`: Enable async processing mode
- `--batch-size N`: Number of requests per batch (default: 10)
- `--max-concurrent N`: Maximum concurrent requests (default: 5)

## Best Practices

### Batch Size Selection

Choose batch size based on:
- **Remote APIs**: 10-50 (depends on rate limits)
- **Local models**: 5-20 (depends on available memory)
- **Resource constraints**: Lower for limited CPU/memory

### Concurrency Tuning

Set max concurrent requests based on:
- **API rate limits**: Stay within provider limits
- **Network latency**: Higher concurrency for high-latency connections
- **Local resources**: Balance with CPU/GPU availability

### Example Configurations

#### High-throughput remote API
```bash
quill fuzz --async --batch-size 50 --max-concurrent 20 \
    -c large_corpus/ -o runs/high_throughput \
    http --url https://fast-api.example.com
```

#### Local Ollama with GPU
```bash
quill fuzz --async --batch-size 10 --max-concurrent 4 \
    -c test_corpus/ -o runs/gpu_test \
    ollama --model mixtral
```

#### Rate-limited API
```bash
quill fuzz --async --batch-size 5 --max-concurrent 2 \
    -c corpus.txt -o runs/rate_limited \
    http --url https://limited-api.example.com
```

## Monitoring Performance

The async fuzzer provides real-time performance metrics:

```
Progress: 500/1000 prompts (45.2 prompts/sec)
```

Compare with sync mode to measure improvement:

```bash
# Sync mode
time quill fuzz -c corpus.txt -o runs/sync_test -n 100 ollama --model llama2

# Async mode  
time quill fuzz --async -c corpus.txt -o runs/async_test -n 100 ollama --model llama2
```

## Troubleshooting

### Connection Errors

If you see connection errors:
1. Reduce `--max-concurrent` value
2. Check API rate limits
3. Verify network connectivity

### Memory Issues

For out-of-memory errors:
1. Reduce `--batch-size`
2. Lower `--max-concurrent`
3. Monitor system resources

### Timeout Errors

For frequent timeouts:
1. Increase timeout in code (default: 30s)
2. Reduce batch size
3. Check model/API performance

## Implementation Details

The async fuzzer uses:
- `aiohttp` for async HTTP requests
- Connection pooling for efficiency
- Configurable timeout handling
- Graceful error recovery

Results are identical to sync mode - only the processing method differs.