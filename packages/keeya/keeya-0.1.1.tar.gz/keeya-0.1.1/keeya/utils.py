"""
Utility functions for Keeya.
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
        pass

def get_api_key():
    """Get API key with fallback to free service key."""
    # Try user's API key first
    user_key = os.getenv('OPENROUTER_API_KEY')
    if user_key and user_key != 'your_openrouter_key_here':
        return user_key
    
    # Fallback to free service key for users without their own key
    return "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"  # Ignore errors if .env file doesn't exist

# Load .env file when module is imported
load_env()


def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze DataFrame structure and content for AI context.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        dict: Analysis results
    """
    try:
        analysis = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_count': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
            'sample_data': df.head(3).to_dict(),
            'statistical_summary': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
        }
        return analysis
    except Exception as e:
        return {'error': f"Failed to analyze DataFrame: {str(e)}"}


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
        # Get API key (with fallback to free service)
        api_key = get_api_key()
        
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
    # Model configurations
    models = {
        "fast": {
            "name": "openai/gpt-oss-20b:free",
            "description": "GPT-OSS-20B Free (2-4 seconds)",
            "max_tokens": 1000,
            "complexity_threshold": 50
        },
        "balanced": {
            "name": "qwen/qwen-2.5-coder-32b-instruct:free",
            "description": "Qwen 2.5 Coder 32B Free (3-6 seconds)",
            "max_tokens": 1500,
            "complexity_threshold": 100
        },
        "powerful": {
            "name": "qwen/qwen3-coder:free",
            "description": "Qwen3 Coder Free (6-12 seconds)",
            "max_tokens": 2000,
            "complexity_threshold": 200
        }
    }
    
    # Calculate task complexity
    complexity = calculate_task_complexity(system_prompt, user_prompt)
    
    # Select model based on complexity
    if complexity <= models["fast"]["complexity_threshold"]:
        selected = models["fast"]
    elif complexity <= models["balanced"]["complexity_threshold"]:
        selected = models["balanced"]
    else:
        selected = models["powerful"]
    
    print(f"🧠 Selected model: {selected['description']} (complexity: {complexity})")
    return selected["name"]


def calculate_task_complexity(system_prompt: str, user_prompt: str) -> int:
    """
    Calculate task complexity based on prompt content.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        
    Returns:
        int: Complexity score
    """
    complexity = 0
    
    # Base complexity from prompt length
    complexity += len(user_prompt) // 10
    
    # Complexity indicators
    complex_keywords = [
        "machine learning", "model training", "neural network", "deep learning",
        "statistical analysis", "correlation", "regression", "classification",
        "data preprocessing", "feature engineering", "hyperparameter",
        "cross validation", "ensemble", "clustering", "dimensionality reduction"
    ]
    
    for keyword in complex_keywords:
        if keyword.lower() in user_prompt.lower():
            complexity += 20
    
    # DataFrame size complexity
    if "DataFrame" in user_prompt:
        # Look for shape information
        if "Shape:" in user_prompt:
            try:
                # Extract shape info (basic parsing)
                lines = user_prompt.split('\n')
                for line in lines:
                    if "Shape:" in line:
                        shape_part = line.split("Shape:")[1].strip()
                        if "x" in shape_part or "," in shape_part:
                            complexity += 10
                        break
            except:
                pass
    
    # Task type complexity
    if "clean" in system_prompt.lower():
        complexity += 15
    elif "analyze" in system_prompt.lower():
        complexity += 25
    elif "visualize" in system_prompt.lower():
        complexity += 20
    elif "train" in system_prompt.lower():
        complexity += 40
    
    return max(complexity, 10)  # Minimum complexity


def get_available_models() -> Dict[str, str]:
    """
    Get available models with their descriptions.
    
    Returns:
        dict: Model names and descriptions
    """
    return {
        "openai/gpt-oss-20b:free": "GPT-OSS-20B Free (2-4 seconds) - Fast fallback",
        "qwen/qwen-2.5-coder-32b-instruct:free": "Qwen 2.5 Coder 32B Free (3-6 seconds) - Sweet spot",
        "qwen/qwen3-coder:free": "Qwen3 Coder Free (6-12 seconds) - Worth the wait for complex tasks"
    }


def execute_code_safely(code: str, context: Dict[str, Any] = None) -> Any:
    """
    Safely execute generated Python code.
    
    Args:
        code: Python code to execute
        context: Context variables (like df, target, etc.)
        
    Returns:
        Execution result
    """
    try:
        # Create safe execution environment
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'any': any,
                'all': all,
            },
            'pd': pd,
            'pandas': pd,
            'np': __import__('numpy'),
            'numpy': __import__('numpy'),
            'plt': __import__('matplotlib.pyplot'),
            'sns': __import__('seaborn'),
            'sklearn': __import__('sklearn'),
        }
        
        # Add context variables
        if context:
            safe_globals.update(context)
        
        # Execute code
        exec(code, safe_globals)
        
        # Try to return the result (look for common result variables)
        result_vars = ['result', 'cleaned_df', 'analysis_results', 'model', 'df', 'cleaned_data', 'output']
        for var in result_vars:
            if var in safe_globals:
                return safe_globals[var]
        
        # If no specific result variable found, return the last executed expression
        # This handles cases where the code doesn't assign to a variable
        if 'result' not in safe_globals:
            # Try to execute the code and capture the last expression
            try:
                # If the code is a single expression, evaluate it
                if not any(line.strip().startswith(('def ', 'class ', 'import ', 'from ')) for line in code.split('\n') if line.strip()):
                    result = eval(code, safe_globals)
                    return result
            except:
                pass
        
        # If no specific result variable found, return None
        return None
        
    except Exception as e:
        raise Exception(f"Failed to execute code safely: {str(e)}")
