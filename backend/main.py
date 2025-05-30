from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io

app = FastAPI()

# CORS para permitir requisições do app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega o modelo treinado no Teachable Machine (ajuste caminho se necessário)
model = load_model("modelo/keras_model.h5", compile=False)

# Carrega as classes treinadas do arquivo labels.txt
with open("modelo/labels.txt", "r") as f:
    classes = [line.strip() for line in f.readlines()]

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Ajusta para o tamanho esperado pelo modelo (normalmente 224x224)
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    class_name = classes[predicted_class]

    return {"class": class_name}
