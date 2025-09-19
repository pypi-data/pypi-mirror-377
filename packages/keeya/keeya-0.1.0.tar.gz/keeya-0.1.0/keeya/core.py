"""
Core Keeya functionality - AI-powered code generation and execution.
"""

import pandas as pd
import requests
import json
import os
from typing import Any, Optional, Union
from .utils import call_openrouter_api, analyze_dataframe, execute_code_safely
from .prompts import GENERATE_PROMPT, CLEAN_PROMPT, ANALYZE_PROMPT, VISUALIZE_PROMPT, ML_PROMPT


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
        # Call OpenRouter API with generate prompt
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
    AI-powered data cleaning.
    
    Args:
        df: DataFrame to clean
        model: Model to use (optional, auto-selects if None)
        
    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    try:
        # Analyze DataFrame for context
        df_context = analyze_dataframe(df)
        
        # Create context-aware prompt
        context_prompt = f"""
        Clean this DataFrame:
        
        DataFrame Info:
        - Shape: {df.shape}
        - Columns: {list(df.columns)}
        - Data types: {df.dtypes.to_dict()}
        - Missing values: {df.isnull().sum().to_dict()}
        - Sample data:
        {df.head().to_string()}
        
        Please generate Python code to clean this DataFrame and return the cleaned version.
        """
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=CLEAN_PROMPT,
            user_prompt=context_prompt,
            model=model
        )
        
        # Execute the generated code safely
        cleaned_df = execute_code_safely(response, {'df': df})
        return cleaned_df
        
    except Exception as e:
        raise Exception(f"Failed to clean DataFrame: {str(e)}")


def analyze(df: pd.DataFrame, model: str = None) -> dict:
    """
    AI-powered data analysis.
    
    Args:
        df: DataFrame to analyze
        model: Model to use (optional, auto-selects if None)
        
    Returns:
        dict: Analysis results
    """
    try:
        # Analyze DataFrame for context
        df_context = analyze_dataframe(df)
        
        # Create context-aware prompt
        context_prompt = f"""
        Analyze this DataFrame:
        
        DataFrame Info:
        - Shape: {df.shape}
        - Columns: {list(df.columns)}
        - Data types: {df.dtypes.to_dict()}
        - Sample data:
        {df.head().to_string()}
        
        Please generate Python code to analyze this DataFrame and return analysis results.
        """
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=ANALYZE_PROMPT,
            user_prompt=context_prompt,
            model=model
        )
        
        # Execute the generated code safely
        analysis_results = execute_code_safely(response, {'df': df})
        return analysis_results
        
    except Exception as e:
        raise Exception(f"Failed to analyze DataFrame: {str(e)}")


def visualize(df: pd.DataFrame, plot_type: Optional[str] = None, model: str = None) -> None:
    """
    AI-powered visualization.
    
    Args:
        df: DataFrame to visualize
        plot_type: Type of plot to create (optional)
        model: Model to use (optional, auto-selects if None)
    """
    try:
        # Analyze DataFrame for context
        df_context = analyze_dataframe(df)
        
        # Create context-aware prompt
        context_prompt = f"""
        Create visualizations for this DataFrame:
        
        DataFrame Info:
        - Shape: {df.shape}
        - Columns: {list(df.columns)}
        - Data types: {df.dtypes.to_dict()}
        - Sample data:
        {df.head().to_string()}
        
        {"Plot type requested: " + plot_type if plot_type else ""}
        
        Please generate Python code to create appropriate visualizations for this DataFrame.
        """
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=VISUALIZE_PROMPT,
            user_prompt=context_prompt,
            model=model
        )
        
        # Execute the generated code safely
        execute_code_safely(response, {'df': df})
        
    except Exception as e:
        raise Exception(f"Failed to create visualizations: {str(e)}")


def train(df: pd.DataFrame, target: str, model: str = None) -> Any:
    """
    AI-powered ML model training.
    
    Args:
        df: DataFrame with features and target
        target: Name of target column
        model: Model to use (optional, auto-selects if None)
        
    Returns:
        Trained model object
    """
    try:
        # Analyze DataFrame for context
        df_context = analyze_dataframe(df)
        
        # Create context-aware prompt
        context_prompt = f"""
        Train a machine learning model on this DataFrame:
        
        DataFrame Info:
        - Shape: {df.shape}
        - Columns: {list(df.columns)}
        - Data types: {df.dtypes.to_dict()}
        - Target column: {target}
        - Sample data:
        {df.head().to_string()}
        
        Please generate Python code to train a machine learning model and return the trained model.
        """
        
        # Call OpenRouter API
        response = call_openrouter_api(
            system_prompt=ML_PROMPT,
            user_prompt=context_prompt,
            model=model
        )
        
        # Execute the generated code safely
        model = execute_code_safely(response, {'df': df, 'target': target})
        return model
        
    except Exception as e:
        raise Exception(f"Failed to train model: {str(e)}")
