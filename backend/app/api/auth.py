from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.user import User
from app.schemas.schemas import UserRegister, UserLogin, UserOut, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if data.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
    if data.mobile:
        if db.query(User).filter(User.mobile == data.mobile).first():
            raise HTTPException(status_code=400, detail="Mobile number already registered")

    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "user"

    user = User(
        mobile=data.mobile,
        email=data.email,
        username=data.username,
        password=get_password_hash(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = None
    if data.email:
        user = db.query(User).filter(User.email == data.email).first()
    if not user and data.mobile:
        user = db.query(User).filter(User.mobile == data.mobile).first()
    if not user and data.username:
        user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return TokenOut(
        access_token=token,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
