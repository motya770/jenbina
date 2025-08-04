"""
Interaction and Communication Submodule

This submodule handles all aspects of the AI's interaction capabilities, including:
- Chat handling and conversation management
- User interaction processing
- Communication protocols
"""

from .chat_handler import (
    handle_chat_interaction,
    basic_needs_to_json,
    create_metadata_from_person_state
)

__all__ = [
    'handle_chat_interaction',
    'basic_needs_to_json',
    'create_metadata_from_person_state'
] 