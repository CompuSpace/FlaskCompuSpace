from app.database import engine, Base
from app.models import *

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("¡Listo!")
