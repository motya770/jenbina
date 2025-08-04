"""
Person Management Submodule

This submodule handles the AI's person representation, including:
- Person state and attributes
- Conversation management
- Message handling
- Communication statistics
"""

from .person import (
    Person,
    Message,
    Conversation
)

__all__ = [
    'Person',
    'Message', 
    'Conversation'
] 