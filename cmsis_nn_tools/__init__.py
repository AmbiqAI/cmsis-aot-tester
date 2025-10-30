"""
CMSIS-NN Tools Package

A comprehensive toolkit for CMSIS-NN testing, model generation, and FVP simulation.
"""

__version__ = "1.0.0"
__author__ = "CMSIS-NN Tools Team"

from .core.pipeline import FullTestPipeline

__all__ = [
    "FullTestPipeline",
]
