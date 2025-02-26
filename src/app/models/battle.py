from typing import List, Optional
from pydantic import BaseModel, Field, validator


class BattleRequest(BaseModel):
    """Request model for creating a new rap battle."""
    rapper_a: str = Field(..., description="Name or description of the first rapper")
    rapper_b: str = Field(..., description="Name or description of the second rapper")
    rounds: int = Field(default=5, description="Number of back-and-forth rounds")
    
    @validator('rounds')
    def validate_rounds(cls, v):
        if v < 1:
            return 1
        if v > 10:
            return 10
        return v


class Verse(BaseModel):
    """A single rap verse within a battle."""
    content: str = Field(..., description="The rap verse content")
    rapper: str = Field(..., description="The rapper who created this verse")


class BattleResponse(BaseModel):
    """Response model containing the battle results."""
    rapper_a: str
    rapper_b: str
    verses: List[Verse] = []
    complete: bool = False
    current_round: int = 0
    total_rounds: int
    id: Optional[str] = None


class BattleSession(BaseModel):
    """Internal model for tracking battle state."""
    rapper_a: str
    rapper_b: str
    verses: List[Verse] = []
    current_round: int = 0
    total_rounds: int
    context: dict = {}


class StreamingVerseResponse(BaseModel):
    """Model for streaming verse responses."""
    verse: str = ""
    rapper: str = ""
    complete: bool = False
    round: int = 0
    error: Optional[str] = None
    battle_id: Optional[str] = None