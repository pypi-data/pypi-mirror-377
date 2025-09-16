# lexi-align

[![PyPI version](https://badge.fury.io/py/lexi-align.svg)](https://badge.fury.io/py/lexi-align)
[![CI](https://github.com/borh-lab/lexi-align/actions/workflows/ci.yaml/badge.svg)](https://github.com/borh-lab/lexi-align/actions/workflows/ci.yaml)

Word alignment of multilingual sentences using structured generation with Large Language Models.

## Installation

Install from PyPI:

```bash
pip install lexi-align
```

(or your favorite method)

The library is API-backend agnostic and only directly depends on [Pydantic](https://docs.pydantic.dev/latest/), so you will need to bring your own API code or use the provided [litellm](https://github.com/BerriAI/litellm) integration.

For LLM support via litellm (recommended), install with the optional dependency:

```bash
pip install lexi-align[litellm]
```

Using uv:

```bash
uv add lexi-align --extra litellm
```

For LLM support via Outlines (for local models), install with:

```bash
pip install lexi-align[outlines]
```

Using uv:

```bash
uv add lexi-align --extra outlines
```

For LLM support via llama.cpp (for local models), install with:

```bash
pip install lexi-align[llama]
```

Using uv:

```bash
uv add lexi-align --extra llama
```

## Usage

### Basic Usage

The library expects pre-tokenized input--it does not perform any tokenization. You must provide tokens as lists of strings:

```python
from lexi_align.adapters.litellm_adapter import LiteLLMAdapter
from lexi_align.core import align_tokens

# Initialize the LLM adapter
llm_adapter = LiteLLMAdapter(model_params={
    "model": "gpt-4o",
    "temperature": 0.0
})

# Provide pre-tokenized input with repeated tokens
source_tokens = ["the", "big", "cat", "saw", "the", "cat"]  # Note: "the" and "cat" appear twice
target_tokens = ["le", "gros", "chat", "a", "vu", "le", "chat"]

result = align_tokens(
    llm_adapter,
    source_tokens,
    target_tokens,
    source_language="English",
    target_language="French"
)

# Access the alignment result
if result.alignment:
    print("Successful alignment:")
    for align in result.alignment.alignment:
        print(f"{align.source_token} -> {align.target_token}")

# Example output will show the uniquified tokens:
# the₁ -> le₁
# big -> gros
# cat₁ -> chat₁
# saw -> a
# saw -> vu
# the₂ -> le₂
# cat₂ -> chat₂
```

### Batched Processing

**EXPERIMENTAL**

For processing multiple sequences efficiently using Outlines (which supports native batching):

```python
from lexi_align.adapters.outlines_adapter import OutlinesAdapter
from lexi_align.core import align_tokens_batched

# Initialize adapter with a local model
llm_adapter = OutlinesAdapter(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",  # or any local model path
    dtype="bfloat16",  # optional: choose quantization
    device="cuda"      # optional: specify device
)

# Multiple sequences to align
source_sequences = [
    ["The", "cat", "sat"],
    ["I", "love", "coding"],
]
target_sequences = [
    ["Le", "chat", "assis"],
    ["J'", "aime", "coder"],
]

# Process in batches
results = align_tokens_batched(
    llm_adapter,
    source_sequences,
    target_sequences,
    source_language="English",
    target_language="French",
    batch_size=2  # Process 2 sequences at a time
)

# Each result contains alignment and diagnostic information
for result in results:
    if result.alignment:
        print(result.alignment.alignment)
    else:
        print("Failed attempts:", len(result.attempts))
```

### Async Processing

**EXPERIMENTAL**

For asynchronous processing:

```python
import asyncio
from lexi_align.adapters.litellm_adapter import LiteLLMAdapter
from lexi_align.core import align_tokens_async

async def align_async():
    llm_adapter = LiteLLMAdapter(model_params={
        "model": "gpt-4o",
        "temperature": 0.0
    })

    source = ["The", "cat", "sat"]
    target = ["Le", "chat", "assis"]

    result = await align_tokens_async(
        llm_adapter,
        source,
        target,
        source_language="English",
        target_language="French"
    )

    return result

# Run async alignment
result = asyncio.run(align_async())
```

### Diagnostic Information

The alignment functions return an `AlignmentResult` object containing both the alignment and diagnostic information:

```python
result = align_tokens(
    llm_adapter,
    source_tokens,
    target_tokens,
    source_language="English",
    target_language="French"
)

# Access the alignment
if result.alignment:
    print("Successful alignment:", result.alignment.alignment)

# Access attempt history
for attempt in result.attempts:
    print(f"Attempt {attempt.attempt_number}:")
    print("Messages sent:", attempt.messages_sent)
    print("Validation passed:", attempt.validation_passed)
    if attempt.validation_errors:
        print("Validation errors:", attempt.validation_errors)
    if attempt.exception:
        print("Exception:", attempt.exception)
```

Note that `AlignmentResult` is returned even if the alignment failed (due to external or internal factors).
Use the above code as a guide to examine the errors.

### Using Custom Guidelines and Examples

You can provide custom alignment guidelines and examples to improve alignment quality:

```python
from lexi_align.adapters.litellm_adapter import LiteLLMAdapter
from lexi_align.core import align_tokens
from lexi_align.models import TextAlignment, TokenAlignment

# Initialize adapter as before
llm_adapter = LiteLLMAdapter(model_params={
    "model": "gpt-4o",
    "temperature": 0.0
})

# Define custom guidelines
guidelines = """
1. Align content words (nouns, verbs, adjectives) first
2. Function words should be aligned when they have clear correspondences
3. Handle idiomatic expressions by aligning all components
4. One source token can align to multiple target tokens and vice versa
"""

# Provide examples to demonstrate desired alignments
examples = [
    (
        "The cat".split(),  # source tokens
        "Le chat".split(),  # target tokens
        TextAlignment(      # gold alignment
            alignment=[
                TokenAlignment(source_token="The", target_token="Le"),
                TokenAlignment(source_token="cat", target_token="chat"),
            ]
        )
    ),
    # Add more examples as needed
]

# Use guidelines and examples in alignment
alignment = align_tokens(
    llm_adapter,
    source_tokens,
    target_tokens,
    source_language="English",
    target_language="French",
    guidelines=guidelines,
    examples=examples
)
```

### Raw Message Control

For more control over the prompt, you can use `align_tokens_raw` to provide custom messages:

```python
from lexi_align.core import align_tokens_raw

custom_messages = [
    {"role": "system", "content": "You are an expert translator aligning English to French."},
    {"role": "user", "content": "Follow these guidelines:\n" + guidelines},
    # Add any other custom messages
]

alignment = align_tokens_raw(
    llm_adapter,
    source_tokens,
    target_tokens,
    custom_messages
)
```

### Token Uniquification

The library automatically handles repeated tokens by adding unique markers:

```python
from lexi_align.utils import make_unique, remove_unique

# Tokens with repeats
tokens = ["the", "cat", "the", "mat"]

# Add unique markers
unique_tokens = make_unique(tokens)
print(unique_tokens)  # ['the₁', 'cat', 'the₂', 'mat']

# Remove markers
original_tokens = remove_unique(unique_tokens)
print(original_tokens)  # ['the', 'cat', 'the', 'mat']
```

You can also customize the marker style:

```python
from lexi_align.text_processing import create_underscore_generator

# Use underscore markers instead of subscripts
marker_gen = create_underscore_generator()
unique_tokens = make_unique(tokens, marker_gen)
print(unique_tokens)  # ['the_1', 'cat', 'the_2', 'mat']
```

### Dynamic Schema Generation

The library now uses dynamic schema generation by default to improve alignment quality and validation:

```python
from lexi_align.adapters.outlines_adapter import OutlinesAdapter
from lexi_align.core import align_tokens

# Initialize adapter - supports dynamic schema by default
llm_adapter = OutlinesAdapter(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    dtype="bfloat16",
    device="cuda",
    batch_size=5  # Enable efficient batching
)

# The library automatically:
# 1. Generates a schema specific to your token sets
# 2. Validates token existence and uniqueness
# 3. Enforces alignment length constraints
# 4. Provides detailed error messages for invalid alignments

result = align_tokens(
    llm_adapter,
    source_tokens,
    target_tokens,
    source_language="English",
    target_language="French"
)

# Check validation results
if result.alignment:
    print("Valid alignment achieved")
else:
    for attempt in result.attempts:
        if attempt.validation_errors:
            print(f"Attempt {attempt.attempt_number} errors:")
            for error_type, msg, tokens in attempt.validation_errors:
                print(f"- {error_type}: {msg}")
```

The dynamic schema:
- Ensures tokens exist in the source/target sets
- Handles repeated tokens with unique markers
- Sets minimum/maximum alignment lengths
- Provides clear error messages for invalid alignments
- Supports partial alignments with retries

### Using Local Models with llama.cpp

For running local models with llama.cpp:

```python
from lexi_align.adapters.llama_cpp_adapter import LlamaCppAdapter
from lexi_align.core import align_tokens

# Initialize the llama.cpp adapter with a local model
llm_adapter = LlamaCppAdapter(
    model_path="path/to/model.gguf",
    n_gpu_layers=-1,  # Use GPU acceleration
)

# Note that for some GGUF models the pre-tokenizer might fail,
# in which case you can specify the tokenizer_repo_id, which
# should point to the base model's repo_id on Huggingface.

# Use the same API as with other adapters
alignment = align_tokens(
    llm_adapter,
    source_tokens,
    target_tokens,
    source_language="English",
    target_language="French"
)
```

### Performance

Here are some preliminary results on the test EN-SL subset of XL-WA (using the older 0.1.0 version):

#### gpt-4o-2024-08-06 (1shot) (seed=42)

| Language Pair | Precision | Recall | F1 |
| --- | --- | --- | --- |
| EN-SL | 0.863 | 0.829 | 0.846 |
| **Average** | **0.863** | **0.829** | **0.846** |

#### claude-3-haiku-20240307 (1shot)

| Language Pair | Precision | Recall | F1 |
| --- | --- | --- | --- |
| EN-SL | 0.651 | 0.630 | 0.640 |
| **Average** | **0.651** | **0.630** | **0.640** |

#### meta-llama/Llama-3.2-3B-Instruct (1shot)

| Language Pair | Precision | Recall | F1 |
| --- | --- | --- | --- |
| EN-SL | 0.606 | 0.581 | 0.593 |
| **Average** | **0.606** | **0.581** | **0.593** |

For reference, the 1-shot (1 example) `gpt-4o-2024-08-06` results for EN-SL outperform all systems presented in the [paper](https://ceur-ws.org/Vol-3596/paper32.pdf) (Table 2).
Smaller LLMs perform below SOTA.

### Pharaoh Format Export

While the core alignment functions work with pre-tokenized input, the Pharaoh format utilities currently assume space-separated tokens when parsing/exporting. If your tokens contain spaces or require special tokenization, you'll need to handle this separately.

```python
from lexi_align.utils import export_pharaoh_format

# Note: Pharaoh format assumes space-separated tokens
# Default separator is tab
pharaoh_format = export_pharaoh_format(
    source_tokens,  # Pre-tokenized list of strings
    target_tokens,  # Pre-tokenized list of strings
    alignment
)

print(pharaoh_format)
# Output (will differ depending on chosen model):
# The cat sat on the mat    Le chat était assis sur le tapis    0-0 1-1 2-2 2-3 3-4 4-5 5-6

# Use custom separator
pharaoh_format = export_pharaoh_format(
    source_tokens,
    target_tokens,
    alignment,
    sep=" ||| "  # Custom separator
)

print(pharaoh_format)
# Output:
# The cat sat on the mat ||| Le chat était assis sur le tapis ||| 0-0 1-1 2-2 2-3 3-4 4-5 5-6
```

The Pharaoh format consists of three tab-separated fields:
1. Source sentence (space-separated tokens)
2. Target sentence (space-separated tokens)
3. Alignments as space-separated pairs of indices (source-target)

### Running Evaluations

The package includes scripts to evaluate alignment performance on the [XL-WA dataset](https://github.com/SapienzaNLP/XL-WA) (CC BY-NC-SA 4.0):

```bash
# Install dependencies
pip install lexi-align[litellm]

# Basic evaluation on a single language pair
python evaluations/xl-wa.py --lang-pairs EN-SL

# Evaluate on all language pairs
python evaluations/xl-wa.py --lang-pairs all

# Full evaluation with custom parameters
python evaluations/xl-wa.py \
    --lang-pairs EN-FR EN-DE \
    --model gpt-4o \
    --temperature 0.0 \
    --seed 42 \
    --num-train-examples 3 \
    --output results.json
```

Available command-line arguments:

- `--lang-pairs`: Language pairs to evaluate (e.g., EN-SL EN-DE) or "all"
- `--model`: LLM model to use (default: gpt-4o)
- `--temperature`: Temperature for LLM sampling (default: 0.0)
- `--seed`: Random seed for example selection (default: 42)
- `--model-seed`: Seed for LLM sampling (optional)
- `--num-train-examples`: Number of training examples for few-shot learning
- `--sample-size`: Number of test examples to evaluate per language pair
- `--output`: Path to save results JSON file
- `--verbose`: Enable verbose logging

## Changelog

### v0.3.0 (2024-03-11)
- Added support for batched processing with `align_tokens_batched`
- Added async support via `align_tokens_async`
- Added enhanced diagnostics and error reporting
- Added alignment visualization tools
- Added token-level analysis and metrics
- Added support for custom marker types (subscript/underscore)
- Added support for custom separators in Pharaoh format
- Improved retry logic and validation
- Added CI and evaluation scripts

### v0.2.x (2024-03-07)
- Added support for local models via Outlines and llama.cpp
- Added retries on errors or invalid alignments
- Added async completion support for litellm
- Added support for model weight quantization
- Added improved error messages and validation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{lexi_align,
  title = {lexi-align: Word Alignment via Structured Generation},
  author = {Hodošček, Bor},
  year = {2024},
  url = {https://github.com/borh-lab/lexi-align}
}
```

## References

We use the XL-WA dataset ([repository](https://github.com/SapienzaNLP/XL-WA)) to perform evaluations:

```bibtex
@InProceedings{martelli-EtAl:2023:clicit,
  author    = {Martelli, Federico  and  Bejgu, Andrei Stefan  and  Campagnano, Cesare  and  Čibej, Jaka  and  Costa, Rute  and  Gantar, Apolonija  and  Kallas, Jelena  and  Koeva, Svetla  and  Koppel, Kristina  and  Krek, Simon  and  Langemets, Margit  and  Lipp, Veronika  and  Nimb, Sanni  and  Olsen, Sussi  and  Pedersen, Bolette Sandford  and  Quochi, Valeria  and  Salgado, Ana  and  Simon, László  and  Tiberius, Carole  and  Ureña-Ruiz, Rafael-J  and  Navigli, Roberto},
  title     = {XL-WA: a Gold Evaluation Benchmark for Word Alignment in 14 Language Pairs},
  booktitle      = {Procedings of the Ninth Italian Conference on Computational Linguistics (CLiC-it 2023)},
  month          = {November},
  year           = {2023}
}
```

This code was spun out of the [hachidaishu-translation](https://github.com/borh/hachidaishu-translation) project, presented at  [JADH2024](https://jadh2024.l.u-tokyo.ac.jp/).

## Development

Contributions are welcome! Please feel free to submit a Pull Request.

To set up the development environment:

```bash
git clone https://github.com/borh-lab/lexi-align.git
cd lexi-align
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```
