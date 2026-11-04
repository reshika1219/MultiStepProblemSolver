from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, require_chat_owner
from app.db.mongo import get_db
from app.repositories.chat_repo import get_chat_state

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("/{chat_id}/uia-state")
async def get_uia_state(chat_id: str, user=Depends(get_current_user)):
    db = get_db()
    await require_chat_owner(db, user, chat_id)
    doc = await get_chat_state(db, chat_id)
    if not doc:
        # Return empty state instead of 404 to simplify UI
        return {
            "chat_id": chat_id,
            "employment_category_id": None,
            "skills_selected": None,
            "let_system_decide": False,
            "vault_version": None
        }
    return doc
