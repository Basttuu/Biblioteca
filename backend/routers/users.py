# backend/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from backend.database import SessionLocal
from backend import models, schemas
from backend.auth import hash_password, verify_password, create_access_token, get_current_user, require_admin, get_db

router = APIRouter(prefix="/users", tags=["Users"])

# Registrar usuario
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuario ya registrado")
    hashed_pwd = hash_password(user.password)
    new_user = models.User(username=user.username, password=hashed_pwd, role="reader")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login (OAuth2 password)
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Obtener usuario logueado
@router.get("/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Listar usuarios (solo admin)
@router.get("/", response_model=list[schemas.User])
def list_users(_admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.User).all()

# Promover usuario a admin (solo admin)
@router.post("/{user_id}/promote")
def promote_user(user_id: int, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    u.role = "admin"
    db.commit()
    return {"msg": f"{u.username} promovido a admin"}

# Editar usuario (solo admin)
@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user_update.username:
        u.username = user_update.username
    if user_update.role:
        u.role = user_update.role

    db.commit()
    db.refresh(u)
    return u
