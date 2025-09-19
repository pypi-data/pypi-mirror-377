"""
Basic usage examples for Keeya.
"""

import keeya
import pandas as pd
import os

def main():
    """Run basic Keeya examples."""
    print("🚀 Keeya Basic Usage Examples")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ OPENROUTER_API_KEY not set!")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='your_key_here'")
        return
    
    try:
        # Example 1: Basic code generation
        print("\n=== Basic Code Generation ===")
        code = keeya.generate("function to add two numbers")
        print("Generated code:")
        print(code)
        
        # Example 2: Data processing function
        print("\n=== Data Processing Function ===")
        code = keeya.generate("function to calculate mean of a list")
        print("Generated code:")
        print(code)
        
        # Example 3: Data science operations
        print("\n=== Data Science Operations ===")
        
        # Create sample data
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'age': [25, 30, 35, 28],
            'salary': [50000, 60000, 70000, 55000]
        })
        
        print("Original DataFrame:")
        print(df)
        
        # AI-powered operations
        print("\n=== AI-Powered Operations ===")
        
        # Test data cleaning
        print("🧹 Testing data cleaning...")
        cleaned_df = keeya.clean(df)
        print("✅ Data cleaning completed")
        print(f"Cleaned DataFrame shape: {cleaned_df.shape}")
        
        # Test data analysis
        print("\n📊 Testing data analysis...")
        analysis = keeya.analyze(df)
        print("✅ Data analysis completed")
        print(f"Analysis keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'Not a dict'}")
        
        # Test visualization
        print("\n📈 Testing visualization...")
        keeya.visualize(df, plot_type='scatter')
        print("✅ Visualization completed")
        
        # Test ML training
        print("\n🤖 Testing ML training...")
        model = keeya.train(df, target='salary')
        print("✅ ML training completed")
        print(f"Model type: {type(model)}")
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your API key and try again")

if __name__ == "__main__":
    main()
