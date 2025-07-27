# Quill - LLM Adversarial Prompt Fuzzer

## Project Overview

Quill is a defensive security testing tool designed to stress-test Large Language Models (LLMs) by generating adversarial prompts through mutation strategies. It helps security researchers and AI developers identify potential vulnerabilities, anomalies, and refusal patterns in LLM responses.

**Primary Purpose**: Test LLM robustness and safety mechanisms by systematically fuzzing prompts to discover edge cases and potential security issues.

## Key Features

- **Adversarial Prompt Generation**: Creates mutated versions of seed prompts to test LLM boundaries
- **Multiple Mutation Strategies**: Supports various mutation techniques including typos and refusal suppression
- **Flexible Client Support**: Works with both HTTP APIs and local Ollama installations
- **Anomaly Detection**: Identifies refusals and unexpected responses using keyword matching
- **Comprehensive Reporting**: Generates interactive HTML reports with filtering and statistics
- **Batch Processing**: Can process hundreds of prompts with configurable parameters

## Architecture

### Core Components

1. **Fuzzer** (`quill/core/fuzzer.py`): Main orchestrator that:
   - Loads corpus prompts from files or uses defaults
   - Applies mutation strategies sequentially
   - Queries the target LLM model
   - Detects anomalies in responses
   - Saves results in JSON format

2. **Mutators** (`quill/core/mutators/`): Pluggable mutation strategies:
   - `typo.py`: Introduces random typing errors (transposition, insertion, deletion)
   - `refusal_suppression.py`: Wraps prompts with instructions to discourage refusals
   - Extensible via `@mutator` decorator for custom strategies

3. **CLI Interface** (`quill/cli.py`): Three main commands:
   - `fuzz`: Run adversarial testing
   - `report`: Generate HTML reports from results
   - `clean`: Remove previous test results

4. **Utilities**:
   - `refusal.py`: Helper to detect refusal patterns in responses
   - `metrics.py`: Calculate success rates and statistics
   - `report.py`: Generate interactive HTML reports
   - `logging.py`: Structured logging with Rich formatting

### Data Flow

1. User provides corpus of seed prompts (or uses defaults)
2. Fuzzer loads prompts and applies mutations
3. Mutated prompts sent to LLM via HTTP or Ollama
4. Responses analyzed for anomalies/refusals
5. Results saved as individual JSON files
6. Summary statistics computed and saved
7. HTML report can be generated from results

## Usage Patterns

### Basic Fuzzing
```bash
# Test with default adversarial prompts
quill fuzz -o runs/test1 --max-prompts 100 ollama --model llama2

# Use custom corpus
quill fuzz -c corpus/safety_tests.txt -o runs/test2 http --url http://api.example.com/v1/chat
```

### Report Generation
```bash
# Generate report from latest run
quill report runs/latest

# Custom output path
quill report runs/test1 -o reports/test1_analysis.html
```

### Cleanup
```bash
# Clean specific directory
quill clean -d runs/test1

# Clean all runs
quill clean --all
```

## Development Guidelines

### Adding New Mutators

1. Create new file in `quill/core/mutators/`
2. Inherit from `Mutator` base class
3. Implement `mutate()` method
4. Register with `@mutator("name")` decorator

Example:
```python
from .base import Mutator, mutator

@mutator("my_strategy")
class MyMutator(Mutator):
    def mutate(self, text: str, *, rng: random.Random) -> str:
        # Your mutation logic here
        return modified_text
```

### Testing Commands

```bash
# Run tests (when implemented)
pytest tests/

# Check code quality
ruff check quill/
ruff format quill/
```

### Output Structure

```
runs/
└── test_run/
    ├── config.json          # Run configuration
    ├── prompt_0000.json     # Individual results
    ├── prompt_0001.json
    ├── ...
    ├── summary.json         # Aggregate statistics
    └── report.html          # Generated report
```

## Security Considerations

- This is a **defensive security tool** for testing LLM safety
- Default corpus contains potentially harmful prompts for testing purposes only
- Should only be used against models you have permission to test
- Results may contain sensitive content - handle with care
- Not intended for bypassing safety measures in production systems

## Common Workflows

### 1. Safety Evaluation
Test a model's refusal mechanisms:
```bash
quill fuzz -c safety_corpus/ -o runs/safety_eval --max-prompts 500 \
  --mutators typo,refusal_suppression ollama --model mixtral
```

### 2. API Endpoint Testing
Test custom LLM API:
```bash
quill fuzz -o runs/api_test http --url https://api.mycompany.com/llm/chat \
  --max-prompts 100 --temperature 0.8
```

### 3. Comparative Analysis
Test multiple models:
```bash
for model in llama2 mistral gemma; do
  quill fuzz -o runs/$model --max-prompts 200 ollama --model $model
  quill report runs/$model -o reports/$model.html
done
```

## Troubleshooting

### Model Not Found (Ollama)
- Check available models: `ollama list`
- Pull required model: `ollama pull model_name`

### Connection Errors
- Verify Ollama is running: `ollama serve`
- Check API endpoint is accessible
- Verify firewall/proxy settings

### Empty Results
- Check corpus file formatting (one prompt per line)
- Verify model is responding correctly
- Check logs with `--verbose` flag

## Future Enhancements

Potential areas for extension:
- Additional mutation strategies (encoding, language mixing, etc.)
- Advanced anomaly detection using ML classifiers
- Integration with other LLM providers (OpenAI, Anthropic, etc.)
- Automated vulnerability classification
- Parallel processing for faster testing
- Result comparison across multiple runs