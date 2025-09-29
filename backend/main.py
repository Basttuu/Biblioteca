# backend/main.py
from fastapi import FastAPI
from backend.database import engine, Base, SessionLocal
from backend import models
from backend.auth import hash_password
from fastapi.staticfiles import StaticFiles
from backend.routers import books, users, loans, recommend

app = FastAPI(title="Biblioteca Digital")

# crear tablas
Base.metadata.create_all(bind=engine)

# crear admin por defecto si no existe
db = SessionLocal()
try:
    if not db.query(models.User).filter(models.User.username == "admin").first():
        admin_user = models.User(username="admin", password=hash_password("admin123"), role="admin")
        db.add(admin_user)
        db.commit()

    # Seed de libros si no existen
    if db.query(models.Book).count() == 0:
        from backend.seed import books_data  # importamos la lista de libros
        for b in books_data:
            book = models.Book(**b)
            db.add(book)
        db.commit()
        print("✅ Seed ejecutado: libros insertados automáticamente")
finally:
    db.close()

# incluir routers
app.include_router(books.router)
app.include_router(users.router)
app.include_router(loans.router)
app.include_router(recommend.router)

# montar frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def root():
    return {"msg": "Bienvenido a la Biblioteca Digital 📚"}
