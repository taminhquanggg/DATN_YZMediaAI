import requests
import cv2
from io import BytesIO
import app.settings as settings
import app.logger as log
import numpy as np

async def upload_image(file, file_name):
    try:
        log.debug("Start upload_image ...")

        _, buffer = cv2.imencode('.jpg', file)
        file_like = BytesIO(buffer)
        file_like.seek(0)

        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUD_ACCOUNT_ID}/images/v1"
        headers = {
            "Authorization": f"Bearer {settings.CLOUD_TOKEN}"
        }
        
        files = {
            "file": (file_name, file_like, "image/jpeg")
        }
        response = requests.post(url, headers=headers, files=files)

        cloudflare_response = response.json()

        if cloudflare_response['success']:
            return {
                "imageCloudID": cloudflare_response['result']['id'],
                "imagePath": cloudflare_response['result']['variants'][0],
            }
        else:
            log.error("Failed upload_image")
            return {}
    except Exception as ex:
        log.error(f"Error upload_image: {ex}")
        return {}

async def get_base_image(imageID):
    try:
        log.debug("Start get_base_image ...")
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUD_ACCOUNT_ID}/images/v1/{imageID}/blob"
        headers = {
            "Authorization": f"Bearer {settings.CLOUD_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            image_data = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            return img
        else:
            log.error("Failed to get_base_image from Cloudflare")
            return None
    except Exception as ex:
        log.error(f"Error get_base_image from Cloudflare: {ex}")
        return None