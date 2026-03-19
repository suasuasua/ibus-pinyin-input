"""
IBus 候选词面板模块
"""

from .candidate_panel import CandidatePanel
from .keyboard_handler import KeyboardHandler
from .panel_config import CandidatePanelConfig, DEFAULT_CONFIG
from .main import IBusCandidatePanel, main

__all__ = [
    'CandidatePanel',
    'KeyboardHandler',
    'CandidatePanelConfig',
    'DEFAULT_CONFIG',
    'IBusCandidatePanel',
    'main',
]

__version__ = '1.0.0'
__author__ = 'IBus Team'
__description__ = 'IBus Chinese Input Method Candidate Panel UI'
