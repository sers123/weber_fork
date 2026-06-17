from datetime import timedelta
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..crud import Crud
from ..schema._user import UserFilter
from ..utils._auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_password

def define_routes(app: FastAPI, crud: Crud) -> None:
    @app.post("/token")
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        users = crud.get_users(UserFilter(user_name=form_data.username))
        if not users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = users[0]
        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_name}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
