from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import imghdr
import PIL.Image
import numpy as np
import json
import base64

NAMESPACE = "production"
MODEL_NAME = "mlops-demo"

def get_internal_service_url(namespace:str, model_name:str):
    internal_service_url = f"http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}"
    return internal_service_url

def is_image_binary(binary: bytes) -> bool:
    image_type = imghdr.what(None, h=binary)
    return image_type is not None

class Image(BaseModel):
    # url: str
    data_b64: str 

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/model")
async def get_model_info():
    url = get_internal_service_url(namespace=NAMESPACE, model_name=MODEL_NAME)
    response = requests.get(url)
    res_json = json.dumps(response.json(), indent=2)
    res_dict = json.loads(res_json)
    return res_dict

@app.get("/model/metadata")
async def get_model_info():
    url = get_internal_service_url(namespace=NAMESPACE, model_name=MODEL_NAME) + "/metadata"
    response = requests.get(url)
    res_json = json.dumps(response.json(), indent=2)
    res_dict = json.loads(res_json)
    return res_dict

@app.post("/classify")
async def post_inference_request(images: List[Image]):
    # LABELS = ["daisy", "dandelion", "roses", "sunflower", "tulip"]
    LABELS = ['both', 'fumi', 'unknown', 'watage']
    url = get_internal_service_url(namespace=NAMESPACE, model_name=MODEL_NAME) + ":predict"
    
    image_byte_list = []
    for image in images:
        # download image from requested url
        # urlData = requests.get(image.url).content
        # is_image_binary(urlData)

        data_binary = base64.b64decode(image.data_b64)

        IMAGE_PATH = "/tmp/image"
        with open(IMAGE_PATH ,mode='wb') as f: # wb でバイト型を書き込める
            f.write(data_binary)

        image = PIL.Image.open(IMAGE_PATH).convert("RGB").resize((299, 299))
        image = np.array(image) / 255
        image_byte = image.tolist()
        image_byte_list.append(image_byte)

    payload = {
        "instances": image_byte_list
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return { "endpoint": url, "response": response.text }

    response_json = json.dumps(response.json(), indent=2)
    response_dict = json.loads(response_json)

    new_predictions = []
    for prediction in response_dict["predictions"]:
        predicted_index = np.argmax(prediction)
        predicted_label = LABELS[predicted_index]
        new_prediction = {
            "prediction_score": dict(zip(LABELS, prediction)),
            "prediction_result": predicted_label
            }
        new_predictions.append(new_prediction)
    
    # new_response_json = json.dumps(new_predictions)

    return new_predictions