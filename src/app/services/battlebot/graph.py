import logging
from typing import AsyncIterator, Dict, List

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from src.app.models.battle import Verse
from src.app.services.battlebot.prompts import (
    SYSTEM_INSTRUCTIONS,
    RAPPER_INSTRUCTIONS,
    FIRST_VERSE_INSTRUCTIONS,
    RESPONSE_VERSE_INSTRUCTIONS,
)
from src.app.utils.logger import setup_logger

logger = setup_logger(name="battle_graph", level=logging.INFO, log_file="battle.log")

MODEL_NAME = "gpt-4o-mini"


class State(TypedDict):
    """State definition for the battle graph."""
    messages: Annotated[list, add_messages]
    verses: List[Verse]
    rapper_a: str
    rapper_b: str
    current_round: int
    total_rounds: int
    current_rapper: str  # Tracks which rapper is currently performing


class BattleGraph:
    def __init__(self, rapper_a: str, rapper_b: str, total_rounds: int = 5):
        """
        Initialize a battle graph for the rap battle.

        Args:
            rapper_a (str): The name/identity of the first rapper
            rapper_b (str): The name/identity of the second rapper
            total_rounds (int): Total number of back-and-forth rounds
        """
        self.rapper_a = rapper_a
        self.rapper_b = rapper_b
        self.total_rounds = total_rounds
        self.llm = ChatOpenAI(model=MODEL_NAME, temperature=0.8)
        self.system_message = SystemMessage(content=SYSTEM_INSTRUCTIONS)
        self.config = {"configurable": {"thread_id": "battle_1"}}
        self.graph = self._build_graph()

    def _generate_verse_node(self, state: State) -> Dict:
        """
        Generate a verse for the current rapper.
        """
        messages = state["messages"]
        current_rapper = state["current_rapper"]
        opponent = state["rapper_b"] if current_rapper == state["rapper_a"] else state["rapper_a"]
        current_round = state["current_round"]
        total_rounds = state["total_rounds"]
        
        # Add system message if it's not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [self.system_message] + messages
        
        # Prepare the prompt based on whether this is the first verse or a response
        if len(state["verses"]) == 0:
            # First verse of the battle
            prompt = (
                RAPPER_INSTRUCTIONS.format(
                    rapper_name=current_rapper,
                    opponent_name=opponent,
                    current_round=current_round,
                    total_rounds=total_rounds
                )
                + "\n\n"
                + FIRST_VERSE_INSTRUCTIONS
            )
        else:
            # Response to previous verse
            previous_verse = state["verses"][-1].content
            prompt = (
                RAPPER_INSTRUCTIONS.format(
                    rapper_name=current_rapper,
                    opponent_name=opponent,
                    current_round=current_round,
                    total_rounds=total_rounds
                )
                + "\n\n"
                + RESPONSE_VERSE_INSTRUCTIONS.format(previous_verse=previous_verse)
            )
        
        try:
            # Add the prompt as a human message
            verse_prompt = HumanMessage(content=prompt)
            response = self.llm.invoke([*messages, verse_prompt])
            
            # Create a verse object
            verse = Verse(content=response.content, rapper=current_rapper)
            
            # Update the state
            state["verses"].append(verse)
            
            # Switch rappers for next turn
            next_rapper = state["rapper_b"] if current_rapper == state["rapper_a"] else state["rapper_a"]
            state["current_rapper"] = next_rapper
            
            # Update round if needed
            if current_rapper == state["rapper_b"]:  # Completed a full round
                state["current_round"] += 1
                
            # Return the updated state
            return {"messages": [response], "verses": state["verses"], "current_rapper": state["current_rapper"], "current_round": state["current_round"]}
            
        except Exception as e:
            logger.error(f"Error in verse generation: {str(e)}")
            raise Exception(f"Error generating verse: {str(e)}")

    def _should_continue(self, state: State) -> str:
        """
        Determine if the battle should continue or end.
        """
        if state["current_round"] > state["total_rounds"]:
            return "end"
        return "generate_verse"

    def _build_graph(self) -> StateGraph:
        """
        Build the graph structure.
        """
        graph_builder = StateGraph(State)

        # Add nodes to the graph
        graph_builder.add_node("generate_verse", self._generate_verse_node)

        # Add conditional edges
        graph_builder.add_conditional_edges(
            "generate_verse",
            self._should_continue,
            {
                "generate_verse": "generate_verse",
                "end": "end"
            }
        )
        
        # Add the end node
        graph_builder.add_node("end", lambda x: x)
        
        # Set the entry point
        graph_builder.set_entry_point("generate_verse")
        
        return graph_builder.compile(checkpointer=MemorySaver())

    async def generate_battle_stream(self) -> AsyncIterator[Dict]:
        """
        Generate the entire rap battle with streaming support.

        Returns:
            AsyncIterator[Dict]: Stream of verses and updates from the battle
        """
        try:
            initial_state = {
                "messages": [],
                "verses": [],
                "rapper_a": self.rapper_a,
                "rapper_b": self.rapper_b,
                "current_round": 1,
                "total_rounds": self.total_rounds,
                "current_rapper": self.rapper_a  # Start with rapper A
            }

            # Stream both values and messages
            async for chunk in self.graph.astream(
                initial_state, self.config, stream_mode=["values", "messages"]
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error in battle generation: {str(e)}")
            raise Exception(f"Error generating battle stream: {str(e)}")


# Factory function to get or create battle graphs
_battle_graphs = {}

def get_battle_graph(battle_id: str, rapper_a: str, rapper_b: str, total_rounds: int = 5) -> BattleGraph:
    """
    Get or create a battle graph.

    Args:
        battle_id (str): Unique identifier for this battle
        rapper_a (str): First rapper name
        rapper_b (str): Second rapper name
        total_rounds (int): Number of rounds in the battle

    Returns:
        BattleGraph: The battle graph instance
    """
    if battle_id not in _battle_graphs:
        _battle_graphs[battle_id] = BattleGraph(rapper_a, rapper_b, total_rounds)
    return _battle_graphs[battle_id]