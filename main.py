from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from tensorflow import keras
import numpy as np
from PIL import Image
import io
import asyncio 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = keras.models.load_model("./modelo/keras_model.h5")
classes = ["vape-box", "pen", "pod", "nao-vape"]

model_lock = asyncio.Lock()

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

    async with model_lock:

        await asyncio.sleep(20)
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction, axis=1)[0]
        class_name = classes[predicted_class]
        confidence = float(np.max(prediction))


    return {"class": class_name, "confidence": confidence}
