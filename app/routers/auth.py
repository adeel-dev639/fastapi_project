from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import database, models, utiils, Oauth2

router = APIRouter()

@router.post('/login')
def login(user_credential: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    # OAuth2PasswordRequestForm has `username` and `password` fields.
    user = db.query(models.User).filter(models.User.email == user_credential.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    if not utiils.verify(user_credential.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    # Generate an access token for the user
    access_token = Oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
