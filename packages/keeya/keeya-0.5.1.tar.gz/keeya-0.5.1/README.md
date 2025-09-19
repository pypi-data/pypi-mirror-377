# Keeya

**AI-Powered Python Library for Code Generation**

Keeya is a simple Python library that uses AI to generate clean, executable Python code on-demand. Unlike traditional code completion tools, Keeya runs in your Python environment and generates production-ready code based on your requirements.

## Installation

```bash
pip install keeya
```

## Setup

**No setup required!** Keeya works out of the box with Google Gemini AI.

**Free Tier:**
- 🚀 **Gemini 2.5 Flash:** Latest model, 1M context window, fast & reliable
- 🧠 **Gemini 2.5 Pro:** Most capable model, high quality output
- ⚡ **Gemini 2.0 Flash Exp:** Cutting-edge experimental model
- 🎯 **High Quality:** Clean, production-ready code generation

## Quick Start

```python
import keeya

# Generate any Python function
code = keeya.generate("function to add two numbers")
print(code)

# Generate complex algorithms
code = keeya.generate("function to implement quicksort")
print(code)
```

## Examples

### Basic Code Generation

```python
import keeya

# Generate any Python function
code = keeya.generate("function to add two numbers")
print(code)
# Output: def add_numbers(a, b): return a + b

# Generate data processing function
code = keeya.generate("function to calculate mean of a list")
print(code)
# Output: def calculate_mean(numbers): return sum(numbers) / len(numbers)
```

### Data Science Operations

```python
import keeya
import pandas as pd

# Load your data
df = pd.read_csv('data.csv')

# AI-powered data cleaning
cleaned_df = keeya.clean(df)

# AI-powered analysis
insights = keeya.analyze(df)

# AI-powered visualization
keeya.visualize(df, plot_type='scatter')

# AI-powered ML training
model = keeya.train(df, target='price')
```

## Features

- **Simple API**: Just call `keeya.generate()` or `keeya.clean()`
- **AI-Powered**: Uses AI to generate code based on your data
- **Context-Aware**: Understands your DataFrames and generates appropriate code
- **Google Gemini Integration**: Powered by Google's advanced AI models
- **Jupyter Ready**: Works seamlessly in notebooks and Colab
- **Safe Execution**: Safely executes generated code and returns results
- **Clean Code Generation**: Produces production-ready Python code with inline comments

## Examples

### Basic Functions

```python
# Generate utility functions
code = keeya.generate("function to reverse a string")
code = keeya.generate("function to find duplicates in a list")
code = keeya.generate("function to sort a dictionary by values")
```

### Data Science

```python
# Data cleaning
cleaned_df = keeya.clean(df)

# Data analysis
analysis = keeya.analyze(df)

# Visualizations
keeya.visualize(df, plot_type='histogram')
keeya.visualize(df, plot_type='correlation')

# Machine learning
model = keeya.train(df, target='target_column')
predictions = model.predict(test_df)
```

## Model Selection

Keeya uses Google Gemini by default, but you can specify different models:

```python
# Use default Gemini 2.5 Flash (latest, fast, 1M context)
code = keeya.generate("function to calculate fibonacci")

# Use Gemini 2.5 Pro (most capable for complex tasks)
code = keeya.generate("complex machine learning pipeline", model="gemini-2.5-pro")

# Use experimental Gemini 2.0 Flash (cutting edge)
code = keeya.generate("advanced algorithm", model="gemini-2.0-flash-exp")

# Get available models
models = keeya.get_available_models()
print(models)
```

## API Reference

### `keeya.generate(prompt, model="gemini-2.5-flash")`
Generate Python code from natural language prompt.

### `keeya.clean(df, model=None)`
AI-powered data cleaning. Returns cleaned DataFrame.

### `keeya.analyze(df, model=None)`
AI-powered data analysis. Returns analysis results.

### `keeya.visualize(df, plot_type=None, model=None)`
AI-powered visualization. Creates and displays plots.

### `keeya.train(df, target, model=None)`
AI-powered ML model training. Returns trained model.

### `keeya.get_available_models()`
Get available models and their descriptions.

## Requirements

- Python 3.8+
- pandas
- requests

## License

MIT License
