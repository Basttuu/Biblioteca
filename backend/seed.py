# backend/seed.py
from backend.database import SessionLocal, engine, Base
from backend import models

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Lista de 30 libros de ejemplo
books_data = [
    {"title": "Cien años de soledad", "author": "Gabriel García Márquez", "genre": "Novela", "review": "Un clásico del realismo mágico."},
    {"title": "Don Quijote de la Mancha", "author": "Miguel de Cervantes", "genre": "Novela", "review": "La gran obra de la literatura española."},
    {"title": "El Principito", "author": "Antoine de Saint-Exupéry", "genre": "Fábula", "review": "Historia poética y filosófica para niños y adultos."},
    {"title": "1984", "author": "George Orwell", "genre": "Distopía", "review": "Crítica a los regímenes totalitarios."},
    {"title": "La Odisea", "author": "Homero", "genre": "Épica", "review": "Una de las grandes epopeyas de la Antigüedad."},
    {"title": "El Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasía", "review": "Aventura en la Tierra Media."},
    {"title": "Harry Potter y la piedra filosofal", "author": "J.K. Rowling", "genre": "Fantasía", "review": "Inicio de la saga del joven mago."},
    {"title": "Orgullo y prejuicio", "author": "Jane Austen", "genre": "Romance", "review": "Clásico de la literatura inglesa."},
    {"title": "Crimen y castigo", "author": "Fiódor Dostoyevski", "genre": "Novela", "review": "Exploración de la culpa y la redención."},
    {"title": "Matar a un ruiseñor", "author": "Harper Lee", "genre": "Novela", "review": "Historia sobre racismo y justicia."},
    {"title": "El código Da Vinci", "author": "Dan Brown", "genre": "Thriller", "review": "Misterio y símbolos ocultos."},
    {"title": "El alquimista", "author": "Paulo Coelho", "genre": "Filosofía", "review": "Búsqueda del destino personal."},
    {"title": "La casa de los espíritus", "author": "Isabel Allende", "genre": "Novela", "review": "Saga familiar con realismo mágico."},
    {"title": "Cumbres borrascosas", "author": "Emily Brontë", "genre": "Romance", "review": "Historia de amor y venganza."},
    {"title": "Frankenstein", "author": "Mary Shelley", "genre": "Ciencia ficción", "review": "Experimento científico y monstruo."},
    {"title": "Drácula", "author": "Bram Stoker", "genre": "Terror", "review": "Clásico de vampiros."},
    {"title": "El retrato de Dorian Gray", "author": "Oscar Wilde", "genre": "Filosofía", "review": "Decadencia y estética."},
    {"title": "Viaje al centro de la Tierra", "author": "Julio Verne", "genre": "Aventura", "review": "Exploración científica y fantástica."},
    {"title": "Veinte mil leguas de viaje submarino", "author": "Julio Verne", "genre": "Aventura", "review": "Viaje con el Capitán Nemo."},
    {"title": "Los miserables", "author": "Victor Hugo", "genre": "Novela histórica", "review": "Redención y justicia social."},
    {"title": "El gran Gatsby", "author": "F. Scott Fitzgerald", "genre": "Novela", "review": "Sueños y decadencia en los años 20."},
    {"title": "Anna Karenina", "author": "León Tolstói", "genre": "Novela", "review": "Amor y tragedia en la Rusia imperial."},
    {"title": "El guardián entre el centeno", "author": "J.D. Salinger", "genre": "Novela", "review": "Adolescencia y rebeldía."},
    {"title": "La metamorfosis", "author": "Franz Kafka", "genre": "Novela", "review": "Transformación y alienación."},
    {"title": "El nombre de la rosa", "author": "Umberto Eco", "genre": "Misterio", "review": "Asesinato en una abadía medieval."},
    {"title": "El señor de los anillos", "author": "J.R.R. Tolkien", "genre": "Fantasía", "review": "La gran saga de la Tierra Media."},
    {"title": "Juego de tronos", "author": "George R.R. Martin", "genre": "Fantasía", "review": "Lucha por el Trono de Hierro."},
    {"title": "Siddhartha", "author": "Hermann Hesse", "genre": "Filosofía", "review": "Búsqueda espiritual y autoconocimiento."},
    {"title": "El diario de Ana Frank", "author": "Ana Frank", "genre": "Memorias", "review": "Reflexiones durante la Segunda Guerra Mundial."},
    {"title": "La tregua", "author": "Mario Benedetti", "genre": "Novela", "review": "Historia de amor en la rutina diaria."},
    {"title": "Rayuela", "author": "Julio Cortázar", "genre": "Novela", "review": "Innovación narrativa y estilo experimental."},
]

# Insertar en DB
db = SessionLocal()
try:
    for b in books_data:
        exists = db.query(models.Book).filter(models.Book.title == b["title"]).first()
        if not exists:
            book = models.Book(**b)
            db.add(book)
    db.commit()
    print("✅ Seed completado: 30 libros insertados (si no existían).")
finally:
    db.close()
