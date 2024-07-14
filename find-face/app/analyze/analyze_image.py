import numpy as np

import app.logger as log
from app.database.models import Face
import uuid
from app.cloud_service import upload_image
import cv2


def draw_on(img, faces):
    dimg = img.copy()
    for i in range(len(faces)):
        face = faces[i]
        box = face.bbox.astype(np.int)
        color = (0, 0, 255)
        cv2.rectangle(dimg, (box[0], box[1]), (box[2], box[3]), color, 2)
        if face.kps is not None:
            kps = face.kps.astype(np.int)
            # print(landmark.shape)
            for l in range(kps.shape[0]):
                color = (0, 0, 255)
                if l == 0 or l == 3:
                    color = (0, 255, 0)
                cv2.circle(dimg, (kps[l][0], kps[l][1]), 1, color, 2)
        cv2.putText(
            dimg,
            str(face.det_score),
            (box[0] - 1, box[1] - 4),
            cv2.FONT_HERSHEY_COMPLEX,
            0.7,
            (0, 255, 0),
            1,
        )

    return dimg


async def analyze_image(img, fa, isInsert=True):
    res_faces = []
    try:
        faces = fa.get(img)

        for _, face in enumerate(faces):
            face.gender = None
            face.age = None

        result_upload_detect = await upload_image(draw_on(img, faces), uuid.uuid4().hex)

        for _, face in enumerate(faces):
            log.debug("Processing face to" + "insert ..." if isInsert else "search ...")

            if isInsert:
                result_upload_face = await upload_image(
                    draw_on(img, [face]), uuid.uuid4().hex
                )

                emb = face.embedding / np.linalg.norm(face.embedding)
                res_faces.append(
                    Face(
                        ImageDetectID=result_upload_detect["imageCloudID"],
                        ImageDetectPath=result_upload_detect["imagePath"],
                        FaceDetectID=result_upload_face["imageCloudID"],
                        FaceDetectPath=result_upload_face["imagePath"],
                        Embedding=emb,
                    )
                )
            else:
                emb = face.embedding / np.linalg.norm(face.embedding)
                res_faces.append(
                    Face(
                        ImageDetectID=result_upload_detect["imageCloudID"],
                        ImageDetectPath=result_upload_detect["imagePath"],
                        Embedding=emb,
                    )
                )
    except Exception as exc:
        log.error(exc)
    finally:
        return res_faces
