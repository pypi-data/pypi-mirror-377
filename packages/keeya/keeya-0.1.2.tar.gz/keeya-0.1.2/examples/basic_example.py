#!/usr/bin/env python3
"""
Basic Keeya Example - Generate Python Code with AI

This example demonstrates how to use Keeya to generate various types of Python code.
"""

import keeya
import os

def main():
    """Run basic Keeya examples."""
    print("🚀 Keeya Basic Example")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ OPENROUTER_API_KEY not set!")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='your_key_here'")
        return
    
    print("✅ API key found")
    print()
    
    # Example 1: Simple function
    print("1️⃣ Generating a simple function...")
    code = keeya.generate("function to add two numbers")
    print("Generated code:")
    print(code)
    print()
    
    # Example 2: Complex algorithm
    print("2️⃣ Generating a complex algorithm...")
    code = keeya.generate("function to implement merge sort algorithm")
    print("Generated code:")
    print(code[:200] + "...")
    print()
    
    # Example 3: Data processing
    print("3️⃣ Generating data processing function...")
    code = keeya.generate("function to calculate statistics of a list")
    print("Generated code:")
    print(code[:200] + "...")
    print()
    
    # Example 4: Show available models
    print("4️⃣ Available AI models:")
    models = keeya.get_available_models()
    for model, description in models.items():
        print(f"  • {model}: {description}")
    print()
    
    print("🎉 Keeya is working perfectly!")
    print("You can now generate any Python code you need!")

if __name__ == "__main__":
    main()
