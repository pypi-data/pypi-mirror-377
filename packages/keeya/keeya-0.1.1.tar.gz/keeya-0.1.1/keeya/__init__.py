"""
Keeya - AI-Powered Python Library for Data Science

Simple library that uses AI to generate and execute code on-demand.
"""

__version__ = "0.1.0"
__author__ = "Keeya Team"

from .core import generate, clean, analyze, visualize, train
from .utils import get_available_models

__all__ = [
    "generate",
    "clean", 
    "analyze",
    "visualize",
    "train",
    "get_available_models"
]
