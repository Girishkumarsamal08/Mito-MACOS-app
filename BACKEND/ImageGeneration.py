import subprocess
import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep


def open_images(prompt):
    folder_path = "DATA"
    prompt = prompt.replace(" ", "_")

    Files = [f"{prompt}{i}.jpg" for i in range(1, 4)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        if not os.path.exists(image_path):  
            print(f"File not found: {image_path}")
            continue
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            subprocess.run(["code", image_path])
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    
    return response.content

async def generate_images(prompt: str):
    tasks = []
    folder_path = "Data"
    os.makedirs(folder_path, exist_ok=True)  

    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  
            file_path = os.path.join(folder_path, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

def GenerateImages(prompt: str):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(generate_images(prompt))
    else:
        asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        with open("FRONTEND/Files/ImageGeneration.data", "r") as f:
            Data = f.read().strip()
        
        if not Data:
            sleep(1)
            continue

        Prompt, Status = Data.split(",")

        if Status.strip().lower() == "true":
            print("Generating Images...")
            GenerateImages(prompt=Prompt)

            with open("FRONTEND/Files/ImageGeneration.data", "w") as f:
                f.write("False,False")
            break
        else:
          
            sleep(1)

    except :
        pass
        
