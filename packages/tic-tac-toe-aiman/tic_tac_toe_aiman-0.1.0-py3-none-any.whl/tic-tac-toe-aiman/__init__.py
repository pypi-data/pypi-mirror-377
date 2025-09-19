# src/tic_tac_toe_aiman/__init__.py


"""
tic_tac_toe_aiman
لعبة X و O مع واجهة رسومية وذكاء اصطناعي مدمج.
"""

__version__ = "0.1.0"

from .game import TicTacToe
from .ui import GameUI

__all__ = ["TicTacToe", "GameUI"]
