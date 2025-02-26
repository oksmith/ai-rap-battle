import uuid
from typing import Dict, List, Any

from src.app.models.battle import Verse


def generate_battle_id() -> str:
    """
    Generate a unique identifier for a battle.
    
    Returns:
        str: A unique battle ID
    """
    return str(uuid.uuid4())


def extract_verses_from_state(state: Dict[str, Any]) -> List[Verse]:
    """
    Extract verse objects from the graph state.
    
    Args:
        state (Dict[str, Any]): The battle graph state
        
    Returns:
        List[Verse]: The list of verse objects
    """
    if not state or "verses" not in state:
        return []
    
    return state["verses"]


def determine_battle_winner(verses: List[Verse], rapper_a: str, rapper_b: str) -> str:
    """
    This is a placeholder function. In a real implementation, you might
    want to use some criteria to determine a winner, or build a UI that lets
    users vote on who won.
    
    Args:
        verses (List[Verse]): The verses from the battle
        rapper_a (str): The name of rapper A
        rapper_b (str): The name of rapper B

    Returns:
        str: The name of the winner or "Tie"
    """
    # This is intentionally simplified. Perhaps we could add real logic here,
    # such as a scoring system, or leave it entirely up to the user.
    return "It's up to you to decide!"
