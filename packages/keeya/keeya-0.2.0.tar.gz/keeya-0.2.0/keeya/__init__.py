"""
Keeya - AI-Powered Python Code Generation

Simple library that uses AI to generate clean, executable Python code.
"""

__version__ = "0.2.0"
__author__ = "Keeya Team"

from .keeya import generate, clean, analyze, visualize, train, get_available_models

__all__ = [
    "generate",
    "clean", 
    "analyze",
    "visualize",
    "train",
    "get_available_models"
]
