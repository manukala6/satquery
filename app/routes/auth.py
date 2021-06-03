import os
from dotenv import load_dotenv
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

from ..models.user import *
from ..routes.users import user_db

load_dotenv()
SECRET = os.environ.get("SECRET")

jwt_authentication = JWTAuthentication(
    secret=SECRET, 
    lifetime_seconds=3600, 
    tokenUrl="auth/jwt/login"
)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)