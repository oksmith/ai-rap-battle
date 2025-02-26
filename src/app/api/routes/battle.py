import json
import logging
import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.app.models.battle import BattleRequest, BattleResponse, StreamingVerseResponse
from src.app.services.battlebot.graph import get_battle_graph
from src.app.utils.logger import setup_logger

logger = setup_logger(name="battle_app", level=logging.INFO, log_file="battle.log")

router = APIRouter()

# Store active battles
active_battles: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=BattleResponse)
async def start_battle(request: BattleRequest):
    """
    Start a new rap battle between two rappers.
    Returns basic battle info with a battle_id.
    """
    try:
        battle_id = str(uuid.uuid4())
        
        # Store basic battle info
        active_battles[battle_id] = {
            "rapper_a": request.rapper_a,
            "rapper_b": request.rapper_b,
            "total_rounds": request.rounds,
            "current_round": 0,
            "verses": []
        }
        
        return BattleResponse(
            rapper_a=request.rapper_a,
            rapper_b=request.rapper_b,
            verses=[],
            complete=False,
            current_round=0,
            total_rounds=request.rounds,
        )
        
    except Exception as e:
        logger.error(f"Error starting battle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/battle/{battle_id}", response_model=BattleResponse)
async def get_battle(battle_id: str):
    """
    Get the current state of a battle.
    """
    if battle_id not in active_battles:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    battle_info = active_battles[battle_id]
    
    return BattleResponse(
        rapper_a=battle_info["rapper_a"],
        rapper_b=battle_info["rapper_b"],
        verses=battle_info["verses"],
        complete=battle_info["current_round"] >= battle_info["total_rounds"],
        current_round=battle_info["current_round"],
        total_rounds=battle_info["total_rounds"]
    )


@router.get("/battle_stream/{battle_id}")
async def stream_battle(battle_id: str):
    """
    Stream a rap battle verse by verse.
    """
    try:
        # Generate a new battle ID if not provided
        if battle_id not in active_battles:
            raise HTTPException(status_code=404, detail="Battle not found")
        
        battle_info = active_battles[battle_id]
        rapper_a = battle_info["rapper_a"]
        rapper_b = battle_info["rapper_b"]
        total_rounds = battle_info["total_rounds"]
        
        async def generate_battle():
            try:
                battle_graph = get_battle_graph(battle_id, rapper_a, rapper_b, total_rounds)
                current_verse_content = ""
                current_rapper = ""
                
                async for chunk in battle_graph.generate_battle_stream():
                    try:
                        if not isinstance(chunk, tuple):
                            logger.error(f"Unexpected chunk format: {chunk}")
                            continue
                            
                        chunk_type, chunk_data = chunk
                        
                        if chunk_type == "messages":
                            # Content is streaming in
                            if chunk_data and len(chunk_data) > 0:
                                current_verse_content += chunk_data[0].content
                                # We don't know the rapper yet, will get it from values
                                response = StreamingVerseResponse(
                                    verse=current_verse_content,
                                    rapper=current_rapper,
                                    complete=False,
                                    round=battle_info["current_round"]
                                )
                                yield json.dumps(response.model_dump()) + "\n"
                                
                        elif chunk_type == "values":
                            # Complete state update
                            if "verses" in chunk_data and len(chunk_data["verses"]) > 0:
                                # Get the latest verse and update our tracking
                                latest_verse = chunk_data["verses"][-1]
                                current_verse_content = latest_verse.content
                                current_rapper = latest_verse.rapper
                                
                                # Update battle info
                                battle_info["verses"] = chunk_data["verses"]
                                battle_info["current_round"] = chunk_data.get("current_round", 0)
                                
                                # Send complete verse
                                response = StreamingVerseResponse(
                                    verse=current_verse_content,
                                    rapper=current_rapper,
                                    complete=True,
                                    round=battle_info["current_round"]
                                )
                                yield json.dumps(response.model_dump()) + "\n"
                                
                                # Reset for next verse
                                current_verse_content = ""
                    
                    except Exception as e:
                        logger.error(f"Error processing chunk: {chunk}, error: {e}")
                        yield json.dumps({"error": str(e)}) + "\n"
                        continue
                        
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield json.dumps({"error": str(e)}) + "\n"
                
        return StreamingResponse(generate_battle(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error setting up battle stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))