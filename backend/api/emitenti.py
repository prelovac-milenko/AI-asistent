from fastapi import APIRouter, HTTPException
from redis_client import get_redis
from services.scraper import fetch_emitenti
import json
from config import TTL_SECONDS

router = APIRouter()

@router.get("/emitenti")
async def get_emitenti():
    redis = get_redis()
    key = "emitenti:list"

    # Provjeri keš
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)

    try:
        emitenti_data = fetch_emitenti()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Sačuvaj u Redis sa TTL
    await redis.set(key, json.dumps(emitenti_data), ex=TTL_SECONDS)
    return emitenti_data
