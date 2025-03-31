from fastapi import APIRouter, HTTPException, Body
from redis_client import get_redis
from services.ai import ask_ai
import json

router = APIRouter()

@router.post("/odgovor")
async def generate_odgovor(
    emitent: str = Body(...),
    godine: list[int] = Body(...),
    pitanje: str = Body(...)
):
    redis = get_redis()
    data = {}

    for godina in godine:
        key = f"bilansi:{emitent}:{godina}"
        cached = await redis.get(key)
        if cached:
            data[str(godina)] = json.loads(cached)
        else:
            raise HTTPException(status_code=404, detail=f"Nema keširanih podataka za {emitent} {godina}")

    try:
        odgovor = ask_ai(emitent, data, pitanje)
        return {"odgovor": odgovor}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
