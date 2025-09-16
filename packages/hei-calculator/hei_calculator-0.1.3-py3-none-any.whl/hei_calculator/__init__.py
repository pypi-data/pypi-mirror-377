"""
hei_calculator
--------------

A Python package to calculate Healthy Eating Index (HEI-2015) scores 
from dietary intake data in CSV files.

Usage:
    from hei_calculator import process_csv

    process_csv("input.csv", "output.csv")
"""

from .hei import process_csv

__all__ = ["process_csv"]
__version__ = "0.1.0"
