# backend/routers/recommend.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter(prefix="/recommend", tags=["IA"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{book_id}")
def recommend_books(book_id: int, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    if not books:
        raise HTTPException(status_code=404, detail="No hay libros en la base")

    # Representar libros como textos concatenados
    docs = [f"{b.title} {b.author} {b.genre} {b.review}" for b in books]

# Vectorización TF-IDF (sin stopwords o con lista manual en español)
    spanish_stopwords = ["el", "la", "los", "las", "de", "y", "un", "una", "unos", "unas", "en", "por", "para", "con", "se", "que", "del"]
    vectorizer = TfidfVectorizer(stop_words=spanish_stopwords)
    X = vectorizer.fit_transform(docs)


    # Buscar índice del libro base
    idx = next((i for i, b in enumerate(books) if b.id == book_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    # Calcular similitudes
    similarities = cosine_similarity(X[idx], X).flatten()

    # Tomar los 3 más similares (excepto el mismo)
    similar_indices = similarities.argsort()[-4:-1][::-1]
    recommendations = [books[i] for i in similar_indices if i != idx]

    return [
        {"id": b.id, "title": b.title, "author": b.author, "genre": b.genre}
        for b in recommendations
    ]
