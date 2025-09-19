#!/usr/bin/env python3
"""
Model Selection Demo for Keeya.

This demo shows how Keeya automatically selects the best model
based on task complexity, and how to manually specify models.
"""

import keeya
import pandas as pd
import os
import time

def demo_model_selection():
    """Demonstrate automatic model selection."""
    print("🧠 Keeya Model Selection Demo")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ OPENROUTER_API_KEY not set!")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='your_key_here'")
        return
    
    # Show available models
    print("\n📋 Available Models:")
    models = keeya.get_available_models()
    for model, description in models.items():
        print(f"  • {model}: {description}")
    
    # Test 1: Simple task (should use fast model)
    print("\n🚀 Test 1: Simple Task (should use GPT-OSS-20B)")
    print("-" * 40)
    
    start_time = time.time()
    code = keeya.generate("function to add two numbers")
    end_time = time.time()
    
    print(f"Generated code: {code[:100]}...")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Test 2: Medium complexity task (should use balanced model)
    print("\n⚖️ Test 2: Medium Complexity (should use Qwen2.5-32B)")
    print("-" * 40)
    
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 30, 35, 28],
        'salary': [50000, 60000, 70000, 55000]
    })
    
    start_time = time.time()
    cleaned_df = keeya.clean(df)
    end_time = time.time()
    
    print(f"Cleaned DataFrame shape: {cleaned_df.shape}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Test 3: Complex task (should use powerful model)
    print("\n🔥 Test 3: Complex Task (should use Qwen3-480B)")
    print("-" * 40)
    
    start_time = time.time()
    model = keeya.train(df, target='salary')
    end_time = time.time()
    
    print(f"Model type: {type(model)}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Test 4: Manual model selection
    print("\n🎯 Test 4: Manual Model Selection")
    print("-" * 40)
    
    print("Using GPT-OSS-20B for fast response:")
    start_time = time.time()
    code = keeya.generate("function to calculate fibonacci", model="gpt-oss-20b")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    print("\nUsing Qwen3-480B for complex analysis:")
    start_time = time.time()
    analysis = keeya.analyze(df, model="qwen3-480b")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    print("\n🎉 Model selection demo completed!")

def demo_complexity_analysis():
    """Demonstrate complexity analysis."""
    print("\n🔍 Complexity Analysis Demo")
    print("=" * 50)
    
    # Test different prompt complexities
    prompts = [
        ("Simple", "function to add two numbers"),
        ("Medium", "function to calculate correlation between two columns in a DataFrame"),
        ("Complex", "implement a machine learning pipeline with feature engineering, cross-validation, and hyperparameter tuning for a regression problem")
    ]
    
    for complexity, prompt in prompts:
        print(f"\n📝 {complexity} Prompt: {prompt[:50]}...")
        
        # This would normally show the complexity calculation
        # For demo purposes, we'll just show the prompt
        print(f"   Prompt length: {len(prompt)} characters")
        
        # In real usage, this would call the API
        print(f"   Expected model: {'GPT-OSS-20B' if complexity == 'Simple' else 'Qwen2.5-32B' if complexity == 'Medium' else 'Qwen3-480B'}")

if __name__ == "__main__":
    try:
        demo_model_selection()
        demo_complexity_analysis()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Please check your API key and try again")
