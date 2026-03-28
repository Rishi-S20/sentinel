"""Auth routes — to be implemented in Phase 1."""

from fastapi import APIRouter, Depends, HTTPException, Request
import jwt
from jwt import PyJWKClient


from app.config import settings



router = APIRouter()

jwks_client = PyJWKClient(
    f"https://api.stack-auth.com/api/v1/projects/{settings.STACK_PROJECT_ID}/.well-known/jwks.json"
)

async def get_current_user(request: Request) -> dict:
    token = request.headers.get("x-stack-access-token")
    if not token:
        raise HTTPException(status_code = 401, detail="Missing access token")
    

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience=settings.STACK_PROJECT_ID,
        )
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    return {"id": user["sub"], "email": user.get("email"), "name": user.get("name")}