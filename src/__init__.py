"""
Guardian - AI Safety System for Crisis Detection and Resource Provision

A comprehensive system for detecting mental health crises, domestic violence,
and other safety situations, while preventing AI hallucination of fake crisis resources.
"""

from .guardian import Guardian
from .pattern_detector import PatternDetector
from .hallucination_detector import HallucinationDetector

__version__ = "1.0.0"
__all__ = ["Guardian", "PatternDetector", "HallucinationDetector"]
