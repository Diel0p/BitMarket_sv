"""
Auth Routes
-----------
POST /auth/register    â€” Create account (buyer or seller)
POST /auth/login       â€” Login and receive JWT token
GET  /auth/me          â€” Get current user profile (requires token)
PUT  /auth/me          â€” Update profile (requires token)
"""

from fastapi import APIRouter
from app.app.controllers import auth_controller

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.post("/register", summary="Register a new user account")(auth_controller.register)
router.post("/login",    summary="Login and receive a JWT token")(auth_controller.login)
router.get("/me",        summary="Get the currently authenticated user")(auth_controller.me)
router.put("/me",        summary="Update profile name or phone")(auth_controller.update_profile)

