from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tensorflow import keras
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from PIL import Image
import numpy as np
import io
import asyncio
import os

# Configuração do app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria pasta uploads
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ---------- Configuração do banco ----------
DATABASE_URL = "sqlite:///./postagens.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Modelo de Postagem
class Postagem(Base):
    __tablename__ = "postagens"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    foto_url = Column(String, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)

# Cria as tabelas
Base.metadata.create_all(bind=engine)

# ---------- Modelo IA ----------
model = keras.models.load_model("./modelo/keras_model.h5")
classes = ["vape-box", "pen", "pod", "nao-vape"]
# model_lock = asyncio.Lock()

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    class_name = classes[predicted_class]
    confidence = float(np.max(prediction))

    # async with model_lock:
    #     # await asyncio.sleep(120)
    #     prediction = model.predict(img_array)
    #     predicted_class = np.argmax(prediction, axis=1)[0]
    #     class_name = classes[predicted_class]
    #     confidence = float(np.max(prediction))

    return {"class": class_name, "confidence": confidence}

# ---------- Endpoints das postagens ----------
@app.post("/postagens/")
async def criar_postagem(file: UploadFile = File(...), descricao: str = Form(...)):
    # Salva a foto
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Cria nova postagem no banco
    foto_url = f"/uploads/{filename}"
    nova_postagem = Postagem(descricao=descricao, foto_url=foto_url, data=datetime.utcnow())

    db = SessionLocal()
    db.add(nova_postagem)
    db.commit()
    db.refresh(nova_postagem)
    db.close()

    return {"mensagem": "Postagem criada com sucesso!", "postagem": {
        "id": nova_postagem.id,
        "descricao": nova_postagem.descricao,
        "foto_url": nova_postagem.foto_url,
        "data": nova_postagem.data.isoformat()
    }}

@app.get("/postagens/")
async def listar_postagens():
    db = SessionLocal()
    postagens = db.query(Postagem).order_by(Postagem.data.desc()).all()
    db.close()

    # Retorna como lista de dicionários
    return [
        {
            "id": p.id,
            "descricao": p.descricao,
            "foto_url": p.foto_url,
            "data": p.data.isoformat()
        }
        for p in postagens
    ]

@app.get("/")
async def root():
    return {"mensagem": "API online!"}

# Serve as fotos salvas
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
