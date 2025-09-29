# backend/routers/loans.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models, schemas
from backend.auth import get_current_user, require_admin, get_db
from datetime import datetime
from typing import List

router = APIRouter(prefix="/loans", tags=["Loans"])

# Borrow a book (current user)
@router.post("/borrow/{book_id}", response_model=schemas.Loan)
def borrow_book(book_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    # check availability
    active = db.query(models.Loan).filter(models.Loan.book_id == book_id, models.Loan.returned_at == None).first()
    if active:
        raise HTTPException(status_code=400, detail="El libro ya está prestado")
    loan = models.Loan(user_id=current_user.id, book_id=book_id, borrowed_at=datetime.utcnow(), status="borrowed")
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

# Return a loan (user who borrowed OR admin)
@router.post("/return/{loan_id}", response_model=schemas.Loan)
def return_book(loan_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    # only borrower or admin can return
    borrower = db.query(models.User).filter(models.User.id == loan.user_id).first()
    if current_user.id != loan.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para devolver este libro")
    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="El libro ya fue devuelto")
    loan.returned_at = datetime.utcnow()
    loan.status = "returned"
    db.commit()
    db.refresh(loan)
    return loan

# List my loans
@router.get("/my", response_model=List[schemas.Loan])
def my_loans(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    loans = db.query(models.Loan).filter(models.Loan.user_id == current_user.id).all()
    return loans

# List all loans (admin)
@router.get("/", response_model=List[schemas.Loan])
def list_loans(_admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(models.Loan).all()
