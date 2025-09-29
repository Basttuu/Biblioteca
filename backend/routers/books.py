# backend/routers/books.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models, schemas
from backend.auth import get_current_user, require_admin, get_db
from typing import List

router = APIRouter(prefix="/books", tags=["Books"])

# listar libros con campo 'available'
@router.get("/", response_model=List[schemas.Book])
def read_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    active_loans = db.query(models.Loan).filter(models.Loan.returned_at == None).all()
    borrowed_ids = {loan.book_id for loan in active_loans}
    result = []
    for b in books:
        result.append({
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "genre": b.genre,
            "review": b.review,
            "available": (b.id not in borrowed_ids)
        })
    return result

# crear libro (solo admin)
@router.post("/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return { **book.dict(), "id": db_book.id, "available": True }

# actualizar libro (solo admin)
@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    db_book.title = book.title
    db_book.author = book.author
    db_book.genre = book.genre
    db_book.review = book.review
    db.commit()
    # recompute availability
    active_loan = db.query(models.Loan).filter(models.Loan.book_id == db_book.id, models.Loan.returned_at == None).first()
    return {
        "id": db_book.id,
        "title": db_book.title,
        "author": db_book.author,
        "genre": db_book.genre,
        "review": db_book.review,
        "available": (active_loan is None)
    }

# eliminar libro (solo admin)
@router.delete("/{book_id}")
def delete_book(book_id: int, _admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    db.delete(db_book)
    db.commit()
    return {"msg": f"Libro con id {book_id} eliminado"}
