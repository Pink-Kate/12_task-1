from fastapi import FastAPI, Depends, HTTPException, Query, status, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
import auth
from database import engine, get_db
from config import settings
from rate_limiter import check_rate_limit
from cloudinary_utils import upload_avatar, delete_avatar
import time

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contacts API",
    description="REST API для управління контактами з аутентифікацією",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Аутентифікація та авторизація"
        },
        {
            "name": "contacts",
            "description": "Операції з контактами"
        },
        {
            "name": "search",
            "description": "Пошук контактів"
        },
        {
            "name": "birthdays",
            "description": "Дні народження"
        },
        {
            "name": "users",
            "description": "Управління користувачами"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для правильного кодування UTF-8
@app.middleware("http")
async def add_utf8_headers(request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["root"])
def read_root():
    return FileResponse("templates/index.html", media_type="text/html; charset=utf-8")

@app.get("/web", tags=["web"])
def web_interface():
    return FileResponse("templates/index.html", media_type="text/html; charset=utf-8")

# Authentication endpoints
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує"
        )
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token, tags=["auth"])
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, email=user_credentials.email, password=user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний email або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email не підтверджено. Перевірте вашу пошту для підтвердження.",
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh", response_model=schemas.Token, tags=["auth"])
def refresh_token(token_request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    token_data = auth.verify_token(token_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.get("/verify-email", tags=["auth"])
def verify_email(token: str, db: Session = Depends(get_db)):
    user = crud.verify_user_email(db, token=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    return {"message": "Email successfully verified"}

@app.post("/resend-verification", tags=["auth"])
def resend_verification_email(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
    from email_utils import generate_verification_token, send_verification_email
    new_token = generate_verification_token()
    user.verification_token = new_token
    db.commit()
    
    send_verification_email(email, new_token)
    return {"message": "Verification email sent"}

# User management endpoints
@app.put("/users/avatar", response_model=schemas.User, tags=["users"])
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Read file content
    content = await file.read()
    
    # Upload to Cloudinary
    avatar_url = upload_avatar(content, current_user.id)
    
    # Update user avatar
    updated_user = crud.update_user_avatar(db, current_user.id, avatar_url)
    
    return updated_user

@app.delete("/users/avatar", tags=["users"])
def delete_user_avatar(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Delete from Cloudinary
    delete_avatar(current_user.id)
    
    # Update user avatar to None
    updated_user = crud.update_user_avatar(db, current_user.id, None)
    
    return {"message": "Avatar deleted successfully"}

# Contact endpoints with rate limiting
@app.post("/contacts/", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED, tags=["contacts"])
def create_contact(
    contact: schemas.ContactCreate, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for contact creation
    check_rate_limit(request, settings.RATE_LIMIT_PER_MINUTE, 60, "contact_create")
    
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.get("/contacts/", response_model=List[schemas.Contact], tags=["contacts"])
def read_contacts(
    skip: int = Query(0, ge=0, description="Кількість записів для пропуску"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальна кількість записів"),
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for contact reading
    check_rate_limit(request, settings.RATE_LIMIT_PER_HOUR, 3600, "contact_read")
    
    contacts = crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts

@app.get("/contacts/{contact_id}", response_model=schemas.Contact, tags=["contacts"])
def read_contact(
    contact_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for contact reading
    check_rate_limit(request, settings.RATE_LIMIT_PER_HOUR, 3600, "contact_read")
    
    contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.Contact, tags=["contacts"])
def update_contact(
    contact_id: int, 
    contact: schemas.ContactUpdate, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for contact updates
    check_rate_limit(request, settings.RATE_LIMIT_PER_MINUTE, 60, "contact_update")
    
    db_contact = crud.update_contact(db, contact_id=contact_id, contact=contact, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.delete("/contacts/{contact_id}", tags=["contacts"])
def delete_contact(
    contact_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for contact deletion
    check_rate_limit(request, settings.RATE_LIMIT_PER_MINUTE, 60, "contact_delete")
    
    success = crud.delete_contact(db, contact_id=contact_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/search/", response_model=List[schemas.Contact], tags=["search"])
def search_contacts(
    query: str = Query(..., description="Пошуковий запит для імені, прізвища або email"),
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for search
    check_rate_limit(request, settings.RATE_LIMIT_PER_HOUR, 3600, "contact_search")
    
    contacts = crud.search_contacts(db, query=query, user_id=current_user.id)
    return contacts

@app.get("/contacts/birthdays/upcoming/", response_model=List[schemas.Contact], tags=["birthdays"])
def get_upcoming_birthdays(
    days: int = Query(7, ge=1, le=365, description="Кількість днів для перегляду"),
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Rate limiting for birthday queries
    check_rate_limit(request, settings.RATE_LIMIT_PER_HOUR, 3600, "contact_birthdays")
    
    contacts = crud.get_upcoming_birthdays(db, user_id=current_user.id, days=days)
    return contacts