# FilterHero


LLM based content filtering optimized for long documents.

Features

- different filtering modes for different use cases for cost/time/accuracy optimzations



## Overview

FilterHero solves the fundamental LLM input/output asymmetry problem - where models can process 50K+ tokens of input but only output 8K tokens. It offers two innovative filtering modes to efficiently extract the content you need.


### Benchmark Results

Comprehensive benchmark results from testing on real documents:

| Framework | Methodology | Model Name | Model Config | Run Count | Doc Length | Avg Line Retain Ratio | Line Retain STD | Avg Elapsed Time (s) | Avg Cost ($) | Avg Input Cost | Avg Output Cost |
|-----------|------------|------------|--------------|-----------|------------|--------------------|-----------------|---------------------|--------------|----------------|-----------------|
| filterhero | extractive | gpt-4o | - | 5 | 980 | 32.78% | 5.59% | 65.94 | 0.0382 | 0.0 | 0.0 |
| filterhero | extractive | gpt-4.1-mini | - | 5 | 980 | 43.06% | 4.57% | 46.88 | 0.0074 | 0.0 | 0.0 |
| filterhero | extractive | gpt-4.1 | - | 5 | 980 | 86.94% | 0.20% | 102.87 | 0.0489 | 0.0 | 0.0 |
| filterhero | extractive | gpt-5-mini | - | 5 | 980 | 86.63% | 1.91% | 85.69 | 0.0818 | 0.0 | 0.0 |
| filterhero | extractive | gpt-5 | - | 5 | 980 | 34.31% | 1.97% | 60.37 | 0.4306 | 0.0 | 0.0 |
| filterhero | **subtractive** | **gpt-4o** | **-** | **5** | **980** | **84.22%** | **3.67%** | **36.01** | **0.0071** | **0.0** | **0.0** |
| filterhero | **subtractive** | **gpt-4.1-mini** | **-** | **5** | **980** | **86.10%** | **0.43%** | **37.35** | **0.0073** | **0.0** | **0.0** |
| filterhero | subtractive | gpt-4.1 | - | 5 | 980 | 84.84% | 2.17% | 35.22 | 0.0072 | 0.0 | 0.0 |
| filterhero | subtractive | gpt-5-mini | - | 5 | 980 | 85.29% | 0.91% | 25.41 | 0.0068 | 0.0 | 0.0 |
| filterhero | subtractive | gpt-5 | - | 5 | 980 | 85.80% | 0.49% | 38.27 | 0.0075 | 0.0 | 0.0 |
| filterhero | extractive | gpt-4o | - | 5 | 538 | 34.80% | 1.92% | 43.99 | 0.0241 | 0.0 | 0.0 |
| filterhero | extractive | gpt-4.1-mini | - | 5 | 538 | 52.90% | 5.79% | 29.80 | 0.0050 | 0.0 | 0.0 |
| filterhero | extractive | gpt-4.1 | - | 5 | 538 | 76.95% | 1.50% | 73.01 | 0.0284 | 0.0 | 0.0 |
| filterhero | extractive | gpt-5-mini | - | 5 | 538 | 62.45% | 13.10% | 48.16 | 0.0488 | 0.0 | 0.0 |
| filterhero | extractive | gpt-5 | - | 5 | 538 | 30.59% | 0.38% | 76.97 | 0.3112 | 0.0 | 0.0 |
| filterhero | **subtractive** | **gpt-4o** | **-** | **5** | **538** | **74.20%** | **2.44%** | **25.23** | **0.0051** | **0.0** | **0.0** |
| filterhero | **subtractive** | **gpt-4.1-mini** | **-** | **5** | **538** | **73.75%** | **0.87%** | **29.95** | **0.0054** | **0.0** | **0.0** |
| filterhero | subtractive | gpt-4.1 | - | 5 | 538 | 73.68% | 2.26% | 28.05 | 0.0055 | 0.0 | 0.0 |
| filterhero | subtractive | gpt-5-mini | - | 5 | 538 | 74.35% | 1.42% | 34.46 | 0.0054 | 0.0 | 0.0 |
| filterhero | subtractive | gpt-5 | - | 5 | 538 | 75.72% | 1.35% | 26.90 | 0.0053 | 0.0 | 0.0 |


## Key Features

### 🎯 Dual Filtering Modes

#### 1. **Extractive Mode** (Traditional)
- LLM directly outputs the filtered content
- Best for small documents or when you need reformatted output
- Returns clean, extracted text

#### 2. **Subtractive Mode** (Innovative)
- LLM outputs deletion instructions instead of content
- **81% cost reduction** compared to extractive mode
- Preserves exact original formatting
- Uses Semantic Section Mapping (SSM) for intelligent content categorization

### 📊 Semantic Section Mapping (SSM)

In subtractive mode, FilterHero employs SSM to:
- Categorize document sections semantically (content, navigation, code, footer, etc.)
- Make intelligent keep/delete decisions based on section properties
- Provide detailed deletion tracking with section names and categories

## Installation

pip install filterhero 

```python

from filterhero import FilterHero, WhatToRetain
```

## Basic Usage

### Quick Start

```python
from filterhero import FilterHero, WhatToRetain

# Initialize FilterHero
filter_hero = FilterHero()

# Define what content to retain
what_to_retain = WhatToRetain(
    name="technical content",
    desc="API documentation, endpoints, and code examples",
    text_rules=[
        "Keep all code examples",
        "Keep API endpoint definitions",
        "Remove navigation and footers"
    ]
)

# Read your document
with open("document.md", "r") as f:
    content = f.read()

# Filter using extractive mode (default)
filter_op = filter_hero.run(
    text=content,
    extraction_spec=what_to_retain,
    filter_strategy="contextual",
    model_name="gpt-4o-mini"
)

print(f"Filtered content: {filter_op.content}")
print(f"Lines retained: {filter_op.retained_line_count}/{filter_op.original_line_count}")
```

### Using Subtractive Mode

```python
# Use subtractive mode for better performance
filter_op = filter_hero.run(
    text=content,
    extraction_spec=what_to_retain,
    filter_strategy="contextual",
    filter_mode="subtractive",  # Enable subtractive mode
    model_name="gpt-4o-mini"
)

# Access the Semantic Section Mapping
print(filter_op.SSM)  # Shows all document sections with categories

# See what was deleted
for deletion in filter_op.deletions_applied:
    print(f"Deleted lines {deletion['start_line']}-{deletion['end_line']}: {deletion['name']}")
```

## Configuration Options

### WhatToRetain Schema

Define extraction specifications with fine-grained control:

```python
spec = WhatToRetain(
    name="product information",           # What you're looking for
    desc="Product details and pricing",   # Detailed description
    text_rules=[                          # Additional extraction rules
        "Include all pricing information",
        "Keep product specifications",
        "Retain customer reviews"
    ],
    include_context_chunk=True            # Include surrounding context
)
```

### Filter Strategies

Choose from different filtering strategies:

- `"contextual"` - Keeps relevant context around matches (default)
- `"relaxed"` - More permissive, errs on the side of inclusion  
- `"strict"` - Only exact matches, minimal context
- `"base"` - Minimal filtering, mostly passthrough

### Model Selection

FilterHero supports various OpenAI models:

```python
models = [
    "gpt-4o",       
    "gpt-4.1-mini",   
    "gpt-4.1",  
    "gpt-5",         
    "gpt-5-mini",   
]
```

## Advanced Features

### Multiple Extraction Specifications

Extract multiple types of content simultaneously:

```python
specs = [
    WhatToRetain(name="api_docs", desc="API documentation"),
    WhatToRetain(name="examples", desc="Code examples"),
    WhatToRetain(name="auth", desc="Authentication info")
]

result = filter_hero.run(
    text=content,
    extraction_spec=specs,  # List of specifications
    filter_mode="subtractive"
)
```

### Chained Filtering

Apply multiple filtering stages sequentially:

```python
stages = [
    ([WhatToRetain(name="technical", desc="All technical content")], "relaxed"),
    ([WhatToRetain(name="api", desc="Just API docs")], "strict"),
]

chain_result = filter_hero.chain(content, stages)

# Access individual stage results
for i, filter_op in enumerate(chain_result.filterops):
    print(f"Stage {i+1}: {filter_op.retained_line_count} lines retained")
```

### Async Operations

For better performance with concurrent operations:

```python
import asyncio

async def filter_documents(documents):
    filter_hero = FilterHero()
    
    tasks = []
    for doc in documents:
        task = filter_hero.run_async(
            text=doc,
            extraction_spec=what_to_retain,
            filter_mode="subtractive"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## Output Format

### FilterOp Result Object

The `run()` method returns a `FilterOp` object with:

```python
result.content              # Filtered text content
result.success              # Boolean success indicator
result.filter_mode          # "extractive" or "subtractive"
result.filter_strategy      # Strategy used
result.original_line_count  # Input line count
result.retained_line_count  # Output line count
result.lines_removed        # Number of lines removed (subtractive only)
result.elapsed_time         # Processing time in seconds
result.usage                # Token usage and costs
result.SSM                  # Semantic Section Mapping (subtractive only)
result.deletions_applied    # Detailed deletion info (subtractive only)
```

### Semantic Section Mapping (SSM) Output

In subtractive mode, access detailed section analysis:

```python
# Print all sections
print(result.SSM)

# Access individual sections
for section in result.SSM.sections:
    print(f"Section: {section.name}")
    print(f"  Lines: {section.start_line}-{section.end_line}")
    print(f"  Category: {section.category}")
    print(f"  Is Content: {section.is_content}")
    print(f"  Is Navigation: {section.is_navigation}")
```

## Performance & Benchmarking

### Running Benchmarks

Use the included benchmark script to test performance:

```python
python benchmark.py
```

This tests:
- Multiple models (gpt-4o, gpt-4o-mini, gpt-4, etc.)
- Both filtering modes (extractive vs subtractive)
- Different document sizes
- Generates CSV report with metrics


### Key Performance Insights

1. **Cost Efficiency**: Subtractive mode shows **81-85% cost reduction** compared to extractive mode
   - Extractive gpt-4o: $0.0382 (980 lines) vs Subtractive: $0.0071 (**81% savings**)
   - Extractive gpt-5: $0.4306 (980 lines) vs Subtractive: $0.0075 (**98% savings**)

2. **Speed Improvement**: Subtractive mode is **40-65% faster**
   - Extractive gpt-4o: 65.94s vs Subtractive: 36.01s (45% faster)
   - Extractive gpt-4.1: 102.87s vs Subtractive: 35.22s (66% faster)

3. **Consistency**: Subtractive mode shows **lower standard deviation** in retention rates
   - More predictable and consistent results across runs
   - Better for production use cases requiring reliability

4. **Model Comparison**:
   - **Best Value**: gpt-4.1-mini in subtractive mode (low cost, good performance)
   - **Best Quality**: gpt-4o in subtractive mode (balanced retention, fast, affordable)
   - **Most Expensive**: gpt-5 in extractive mode ($0.43 per document!)

## Best Practices

### When to Use Extractive Mode

- Small documents (< 250 lines)
- most of the content is unwanted
- Want LLM to synthesize or summarize content
- Output format differs from input

### When to Use Subtractive Mode

- Large documents (> 250 lines)
- Most of the content is desired. 
- Cost-sensitive applications
- Need detailed tracking of what was removed
- Want to understand filtering decisions via SSM

