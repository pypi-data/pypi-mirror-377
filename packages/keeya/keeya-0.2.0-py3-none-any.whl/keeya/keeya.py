"""
Keeya - AI-Powered Python Code Generation
All functionality combined into one file.
"""

import pandas as pd
import requests
import json
import os
from typing import Dict, Any, Optional

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file."""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    except Exception:
        pass  # Ignore errors if .env file doesn't exist

# Load .env file when module is imported
load_env()

# System Prompts
GENERATE_PROMPT = """You are a Python code generator. Generate simple, clean Python code based on the user's request.

Requirements:
- Generate only Python code
- Keep it simple and concise
- No explanations or markdown formatting
- Use clear variable names
- No excessive documentation
- Just the core functionality

Example:
User: "function to add two numbers"
Response: def add_numbers(num1, num2):
    return num1 + num2"""

CLEAN_PROMPT = """You are a data cleaning expert. Generate Python code to clean the provided DataFrame.

Requirements:
- Handle missing values appropriately (fill, drop, or impute)
- Fix data type issues
- Remove duplicates
- Handle outliers
- Standardize column names
- Return clean, production-ready code
- Include data quality checks
- Use pandas best practices

IMPORTANT: Generate executable code that directly cleans the DataFrame and assigns the result to a variable called 'cleaned_df'. Do not generate function definitions.

Example format:
```python
# Clean the DataFrame
cleaned_df = df.copy()
# Apply cleaning operations
cleaned_df = cleaned_df.drop_duplicates()
# ... more cleaning steps
```

The code should:
1. Start with: cleaned_df = df.copy()
2. Apply cleaning operations directly
3. End with the cleaned DataFrame in the 'cleaned_df' variable"""

ANALYZE_PROMPT = """You are a data analysis expert. Generate Python code to analyze the provided DataFrame.

Requirements:
- Perform exploratory data analysis
- Generate statistical summaries
- Identify patterns and insights
- Create visualizations where appropriate
- Return comprehensive analysis results
- Use pandas, numpy, and matplotlib/seaborn

IMPORTANT: Generate executable code that directly analyzes the DataFrame and assigns the result to a variable called 'analysis_results'. Do not generate function definitions.

Example format:
```python
# Analyze the DataFrame
analysis_results = {}
analysis_results['shape'] = df.shape
analysis_results['dtypes'] = df.dtypes.to_dict()
# ... more analysis
```

The code should:
1. Create a dictionary called 'analysis_results'
2. Perform analysis operations directly
3. Store results in the dictionary
4. End with the analysis results in the 'analysis_results' variable"""

VISUALIZE_PROMPT = """You are a data visualization expert. Generate Python code to create meaningful visualizations.

Requirements:
- Create appropriate plots for the data
- Use matplotlib/seaborn
- Include proper labels and titles
- Make plots publication-ready
- Handle different data types appropriately
- Create multiple plot types if beneficial

IMPORTANT: Generate executable code that directly creates visualizations. Do not generate function definitions.

Example format:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Create visualizations
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='column1', y='column2')
plt.title('Scatter Plot')
plt.show()
```

The code should:
1. Import necessary libraries
2. Create plots directly
3. Include proper styling
4. Display the plots"""

ML_PROMPT = """You are a machine learning expert. Generate Python code to train a model on the provided data.

Requirements:
- Perform proper data preprocessing
- Split data into train/test
- Train appropriate model
- Evaluate model performance
- Return trained model
- Use scikit-learn
- Handle different target types (regression/classification)

IMPORTANT: Generate executable code that directly trains a model and assigns the result to a variable called 'model'. Do not generate function definitions.

Example format:
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Prepare data
X = df.drop(columns=[target])
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestRegressor()
model.fit(X_train, y_train)
```

The code should:
1. Import necessary libraries
2. Prepare the data directly
3. Train the model directly
4. Assign the trained model to the 'model' variable"""

# API Functions
def call_openrouter_api(system_prompt: str, user_prompt: str, model: str = None) -> str:
    """
    Call OpenRouter API with smart model selection.
    
    Args:
        system_prompt: System prompt for AI
        user_prompt: User prompt
        model: Model to use (if None, auto-selects based on complexity)
        
    Returns:
        str: AI response
    """
    try:
        # Get API key from environment
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise Exception("OPENROUTER_API_KEY environment variable not set")
        
        # Auto-select model if not specified
        if model is None:
            model = select_best_model(system_prompt, user_prompt)
        
        # OpenRouter API endpoint
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://keeya.ai",
            "X-Title": "Keeya AI Assistant"
        }
        
        # Prepare payload
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # Make API call
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception("No response from OpenRouter API")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to call OpenRouter API: {str(e)}")

def select_best_model(system_prompt: str, user_prompt: str) -> str:
    """
    Select the best model based on task complexity.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        
    Returns:
        str: Selected model name
    """
    complexity = calculate_task_complexity(system_prompt, user_prompt)
    
    # Store complexity for debugging
    select_best_model.last_calculated_complexity = complexity
    
    if complexity < 200:
        model = "openai/gpt-oss-20b:free"
        select_best_model.last_selected_model_description = "GPT-OSS-20B Free (2-4 seconds) - Fast fallback"
    elif complexity < 400:
        model = "qwen/qwen-2.5-coder-32b-instruct:free"
        select_best_model.last_selected_model_description = "Qwen 2.5 Coder 32B Free (3-6 seconds) - Sweet spot"
    else:
        model = "qwen/qwen3-coder:free"
        select_best_model.last_selected_model_description = "Qwen3 Coder Free (6-12 seconds) - Worth the wait for complex tasks"
    
    return model

def calculate_task_complexity(system_prompt: str, user_prompt: str) -> int:
    """
    Calculate task complexity based on prompt analysis.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        
    Returns:
        int: Complexity score
    """
    complexity = 0
    
    # Base complexity from prompt length
    complexity += len(user_prompt) // 10
    
    # Complexity keywords
    complex_keywords = [
        "machine learning", "ml", "neural network", "deep learning",
        "complex", "advanced", "sophisticated", "comprehensive",
        "algorithm", "optimization", "performance", "scalable",
        "production", "enterprise", "robust", "error handling",
        "pipeline", "workflow", "architecture", "design pattern"
    ]
    
    for keyword in complex_keywords:
        if keyword in user_prompt.lower():
            complexity += 50
    
    # Task type complexity
    if "visualization" in user_prompt.lower() or "plot" in user_prompt.lower():
        complexity += 30
    elif "analysis" in user_prompt.lower() or "analyze" in user_prompt.lower():
        complexity += 40
    elif "train" in user_prompt.lower() or "model" in user_prompt.lower():
        complexity += 60
    
    return complexity

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze DataFrame and return basic information.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dict: Analysis results
    """
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "sample_data": df.head(3).to_dict()
    }

def execute_code_safely(code: str, context: Dict[str, Any] = None) -> Any:
    """
    Execute generated code safely.
    
    Args:
        code: Code to execute
        context: Context variables (like DataFrame)
        
    Returns:
        Any: Execution result
    """
    if context is None:
        context = {}
    
    # Safe globals
    safe_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sum": sum,
            "max": max,
            "min": min,
            "abs": abs,
            "round": round,
            "type": type,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "__import__": __import__
        }
    }
    
    # Add context variables
    safe_globals.update(context)
    
    try:
        # Try to execute the code
        exec(code, safe_globals)
        
        # Try to find result variables
        result_vars = ['result', 'output', 'cleaned_df', 'analysis_results', 'model', 'cleaned_data']
        for var in result_vars:
            if var in safe_globals:
                return safe_globals[var]
        
        # If no result variable found, try to evaluate the last expression
        lines = code.strip().split('\n')
        last_line = lines[-1].strip()
        if last_line and not last_line.startswith('#') and not last_line.startswith('import'):
            try:
                return eval(last_line, safe_globals)
            except:
                pass
        
        return None
        
    except Exception as e:
        raise Exception(f"Failed to execute code safely: {str(e)}")

def get_available_models() -> Dict[str, str]:
    """
    Get available models with their descriptions.
    
    Returns:
        Dict: Model names and descriptions
    """
    return {
        "openai/gpt-oss-20b:free": "GPT-OSS-20B Free (2-4 seconds) - Fast fallback",
        "qwen/qwen-2.5-coder-32b-instruct:free": "Qwen 2.5 Coder 32B Free (3-6 seconds) - Sweet spot",
        "qwen/qwen3-coder:free": "Qwen3 Coder Free (6-12 seconds) - Worth the wait for complex tasks"
    }

# Main API Functions
def generate(prompt: str, model: str = None) -> str:
    """
    Generate Python code from natural language prompt.

    Args:
        prompt: Natural language description of what you want to generate
        model: Model to use (optional, auto-selects if None)

    Returns:
        str: Generated Python code
    """
    try:
        response = call_openrouter_api(
            system_prompt=GENERATE_PROMPT,
            user_prompt=prompt,
            model=model
        )
        return response
    except Exception as e:
        raise Exception(f"Failed to generate code: {str(e)}")

def clean(df: pd.DataFrame, model: str = None) -> pd.DataFrame:
    """
    Clean a DataFrame using AI.

    Args:
        df: DataFrame to clean
        model: Model to use (optional, auto-selects if None)

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Clean this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}"
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=CLEAN_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Execute the generated code
        result = execute_code_safely(response, {'df': df})
        
        if result is not None:
            return result
        else:
            raise Exception("No cleaned DataFrame returned from generated code")
            
    except Exception as e:
        raise Exception(f"Failed to clean DataFrame: {str(e)}")

def analyze(df: pd.DataFrame, model: str = None) -> dict:
    """
    Analyze a DataFrame using AI.

    Args:
        df: DataFrame to analyze
        model: Model to use (optional, auto-selects if None)

    Returns:
        dict: Analysis results
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Analyze this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}"
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=ANALYZE_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Execute the generated code
        result = execute_code_safely(response, {'df': df})
        
        if result is not None:
            return result
        else:
            raise Exception("No analysis results returned from generated code")
            
    except Exception as e:
        raise Exception(f"Failed to analyze DataFrame: {str(e)}")

def visualize(df: pd.DataFrame, plot_type: Optional[str] = None, model: str = None) -> None:
    """
    Create visualizations for a DataFrame using AI.

    Args:
        df: DataFrame to visualize
        plot_type: Type of plot to create (optional)
        model: Model to use (optional, auto-selects if None)

    Returns:
        None: Creates and displays plots
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Create visualizations for this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}"
        
        if plot_type:
            user_prompt += f"\n\nPreferred plot type: {plot_type}"
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=VISUALIZE_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Execute the generated code
        execute_code_safely(response, {'df': df})
        
    except Exception as e:
        raise Exception(f"Failed to create visualizations: {str(e)}")

def train(df: pd.DataFrame, target: str, model: str = None) -> Any:
    """
    Train a machine learning model on a DataFrame using AI.

    Args:
        df: DataFrame with training data
        target: Target column name
        model: Model to use (optional, auto-selects if None)

    Returns:
        Any: Trained model
    """
    try:
        # Analyze DataFrame
        df_info = analyze_dataframe(df)
        
        # Create user prompt with DataFrame info
        user_prompt = f"Train a machine learning model on this DataFrame:\n\nDataFrame Info:\n{json.dumps(df_info, indent=2)}\n\nDataFrame:\n{df.head().to_string()}\n\nTarget column: {target}"
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=ML_PROMPT,
            user_prompt=user_prompt,
            model=model
        )
        
        # Execute the generated code
        result = execute_code_safely(response, {'df': df, 'target': target})
        
        if result is not None:
            return result
        else:
            raise Exception("No trained model returned from generated code")
            
    except Exception as e:
        raise Exception(f"Failed to train model: {str(e)}")
