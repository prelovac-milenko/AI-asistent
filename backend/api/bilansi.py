from fastapi import APIRouter, HTTPException, Query
from redis_client import get_redis
from services.bilans_processor import fetch_bilansi
import json
from config import TTL_SECONDS

router = APIRouter()

@router.get("/bilansi/{code}")
async def get_bilansi(code: str, years: list[int] = Query(...)):
    redis = get_redis()
    output = {}

    for year in years:
        key = f"bilansi:{code}:{year}"
        cached = await redis.get(key)

        if cached:
            output[str(year)] = json.loads(cached)
        else:
            try:
                data = fetch_bilansi(code, [year])
                # Keširaj pojedinačnu godinu s TTL-om
                await redis.set(key, json.dumps(data[str(year)]), ex=TTL_SECONDS)
                output[str(year)] = data[str(year)]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    return {
        "emitent": code,
        "izvjestaji": output
    }
