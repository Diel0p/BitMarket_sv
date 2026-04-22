"""
Auth Controller
===============
Thin layer between routes and user_service.
Handles HTTP concerns: request parsing, response shaping.
"""

from fastapi import Depends
from fastapi.responses import JSONResponse

from app.app.config.database import get_db
from app.app.middleware.auth import get_current_user
from app.app.models.user import UserRegisterRequest, UserLoginRequest, UserUpdateRequest
from app.app.services import user_service


async def register(data: UserRegisterRequest, db=Depends(get_db)):
    # Controllers should only orchestrate HTTP concerns and delegate business rules.
    result = await user_service.register_user(data, db)
    return JSONResponse(status_code=201, content={"success": True, **result})


async def login(data: UserLoginRequest, db=Depends(get_db)):
    # Keep response envelope consistent across endpoints for simpler frontend handling.
    result = await user_service.login_user(data, db)
    return {"success": True, **result}


async def me(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}


async def update_profile(
    data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    # Exclude unset fields to avoid overwriting existing profile values with nulls.
    updated = await user_service.update_user_profile(
        current_user["id"], data.model_dump(exclude_none=True), db
    )
    return {"success": True, "user": updated}

