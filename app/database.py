from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia los valores según tu XAMPP/MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost/sistema_inventario"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
