from fastapi import Depends, HTTPException, status, Header
from jose import JWTError
from app.core.security import decode_token
from app.db.mongo import get_db
from app.repositories.user_repo import find_user_by_id
from app.repositories.chats_repo import verify_chat_owner

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    db = get_db()
    user = await find_user_by_id(db, user_id)
    if not user or user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {"id": user_id, "email": user["email"]}

async def require_chat_owner(db, user: dict, chat_id: str) -> None:
    """404 (not 403) so chat ids of other users are not revealed."""
    if not await verify_chat_owner(db, user["id"], chat_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
