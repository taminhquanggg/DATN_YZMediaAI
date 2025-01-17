import urllib
import urllib.request

import cv2
import numpy as np

import app.logger as log
import base64

def url_to_image(url):
    log.debug("Converting url to image")
    try:
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    except Exception as exc:
        log.error(exc)
        return None


def file_to_image(file):
    log.debug("Converting file to image")
    try:
        nparr = np.fromstring(file, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as exc:
        log.error(exc)
        return None

def base64_to_image(encoded_data):
    log.debug("Converting file to image")
    try:
        nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as exc:
        log.error(exc)
        return None

def string_to_nparray(string):
    log.debug("Converting string to nparray")
    try:
        rpr = string.replace("(", "")
        rpr = rpr.replace(")", "")
        res = np.fromstring(rpr, dtype=float, sep=",")
        return res
    except Exception as exc:
        log.error(exc)
        return None
