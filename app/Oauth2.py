from fastapi import Depends,status,HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas,database,models
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth_schema=OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithum
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_time

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        id: str = str(payload.get("user_id"))  # Convert the user ID to string if it's not already
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_curr_users(token:str=Depends(oauth_schema),db:Session=Depends(database.get_db)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail=f"could not validates credential",
                                        headers={"WWW-Authenticate":"Bearer"})
    token=verify_access_token(token,credentials_exception)

    user=db.query(models.User).filter(models.User.id==token.id).first()

    return user