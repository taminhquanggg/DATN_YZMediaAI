from datetime import datetime
from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, insert, text, inspect
from sqlalchemy.orm import sessionmaker
from app.database.models import get_class
from app.database import init as init_db
from app.database import wait as wait_db
from app.analyze import analyze_image
from app.helper import base64_to_image
from app.cloud_service import get_base_image
import app.logger as log
import app.settings as settings
import numpy as np
import insightface
import json
import uuid
import cv2

app = FastAPI(title="Face API")

log.debug("Constructing FaceAnalysis model.")
fa = insightface.app.FaceAnalysis(providers=["CPUExecutionProvider"])
log.debug("Preparing FaceAnalysis model.")
fa.prepare(ctx_id=0, det_size=(640, 640))

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

wait_db(engine)
init_db(engine)


@app.get("/")
async def root():
    json_resp = {"isSuccess": False, "message": "Server Error"}
    assert fa
    json_resp = JSONResponse(
        content={
            "isSuccess": True,
            "message": "Face API Web Service is running ...",
        }
    )

    return json_resp


@app.get("/table")
async def get_list_table():
    log.debug("Calling get-list-table...")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    return JSONResponse(
        content={
            "isSuccess": True,
            "totalRecords": len(table_names),
            "data": table_names,
        }
    )


@app.post("/table/{tableName}")
async def create_new_table(tableName: str):
    log.debug("Calling create-table...")

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if tableName in table_names:
        return JSONResponse(
            content={
                "isSuccess": False,
                "err": {"msgCode": "1001", "msgString": "Tên bảng đã tồn tại"},
            }
        )

    new_table = get_class(tableName)

    new_table.__table__.create(bind=engine)

    new_table.metadata.clear()

    return JSONResponse(content={"isSuccess": True})


@app.delete("/table/{tableName}")
async def delete_table(tableName: str):
    log.debug("Calling delete_table.")

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if tableName not in table_names:
        return JSONResponse(
            content={
                "isSuccess": False,
                "err": {"msgCode": "1001", "msgString": "Tên bảng không tồn tại"},
            }
        )

    new_table = get_class(tableName)

    new_table.__table__.drop(bind=engine)

    new_table.metadata.clear()

    return JSONResponse(content={"isSuccess": True})


@app.post("/face-api/insert-image-by-base64")
async def insert_image_by_base64(request: Request):
    log.debug("Calling insert-image...")

    try:
        session = Session()

        res = await request.json()

        image = base64_to_image(res["image"])
        fa_faces = await analyze_image(image, fa)

        new_table = get_class(res["tableName"])

        for face in fa_faces:
            fa_emb_str = str(json.dumps(face.Embedding.tolist()))
            emb = "cube(ARRAY" + fa_emb_str + ")"

            new_id = uuid.uuid4().hex

            log.debug("Insert embedding id: " + str(new_id))

            with engine.connect() as conn:
                stmt = insert(new_table).values(
                    ID=new_id,
                    ImageID=res["imageID"],
                    ImageDetectID=face.ImageDetectID,
                    ImageDetectPath=face.ImageDetectPath,
                    FaceDetectID=face.FaceDetectID,
                    FaceDetectPath=face.FaceDetectPath,
                    CreateAt=datetime.today(),
                )

                conn.execute(stmt)

            update_query = text(
                f"UPDATE public.\"{res['tableName']}\" SET \"Embedding\" = "
                + emb
                + ' WHERE "ID" = \''
                + str(new_id)
                + "';"
            )

            session.execute(update_query)
            session.commit()

            new_table.metadata.clear()

        session.close()
        return JSONResponse(content={"isSuccess": True})
    except Exception as ex:
        return JSONResponse(
            content={
                "isSuccess": False,
                "err": {"msgCode": "1001", "msgString": ex},
            }
        )


@app.post("/face-api/insert-image")
async def insert_image(request: Request):
    log.debug("Calling insert-image...")

    try:
        session = Session()

        res = await request.json()

        image = await get_base_image(res["imageID"])

        fa_faces = await analyze_image(image, fa)

        new_table = get_class(res["tableName"])

        set_result = {}

        for face in fa_faces:
            fa_emb_str = str(json.dumps(face.Embedding.tolist()))
            emb = "cube(ARRAY" + fa_emb_str + ")"

            new_id = uuid.uuid4().hex

            log.debug(f"Insert embedding id: {str(new_id)}")

            with engine.connect() as conn:
                stmt = insert(new_table).values(
                    ID=new_id,
                    ImageID=res["imageID"],
                    ImageDetectID=face.ImageDetectID,
                    ImageDetectPath=face.ImageDetectPath,
                    FaceDetectID=face.FaceDetectID,
                    FaceDetectPath=face.FaceDetectPath,
                    CreateAt=datetime.today(),
                )

                conn.execute(stmt)

            update_query = text(
                f"UPDATE public.\"{res['tableName']}\" SET \"Embedding\" = "
                + emb
                + ' WHERE "ID" = \''
                + str(new_id)
                + "';"
            )

            session.execute(update_query)
            session.commit()

            new_table.metadata.clear()

        session.close()

        if len(fa_faces) > 0:
            set_result = {
                "ImageDetectID": fa_faces[0].ImageDetectID,
                "ImageDetectPath": fa_faces[0].ImageDetectPath,
            }

        return JSONResponse(
            content={
                "isSuccess": True,
                "item": jsonable_encoder(set_result),
            }
        )
    except Exception as ex:
        return JSONResponse(
            content={
                "isSuccess": False,
                "err": {"msgCode": "1001", "msgString": ex},
            }
        )


@app.post("/face-api/search-face-by-base64")
async def search_face_by_base64(request: Request):
    log.debug("Calling search_faces.")

    session = Session()

    res = await request.json()

    image = base64_to_image(res["image"])

    fa_faces = await analyze_image(image, fa, False)

    set_result = set()

    for inp_face in fa_faces:
        fa_emb_str = str(json.dumps(inp_face.Embedding.tolist()))
        emb = "cube(ARRAY" + fa_emb_str + ")"

        query = text(
            'SELECT sub."ImageID" '
            "FROM "
            "( "
            'SELECT "ImageID", (1-(POWER(( "Embedding" <-> '
            + emb
            + " ),2)/2))*100 AS similarity "
            f"FROM public.\"{res['tableName']}\" "
            ") AS sub "
            "WHERE sub.similarity > 50 "
            "ORDER BY sub.similarity DESC;"
        )

        query_res = session.execute(query)

        rows_proxy = query_res.fetchall()

        set_result.update([row[0] for row in rows_proxy])

    list_result = list(set_result)

    session.close()
    return JSONResponse(
        content={
            "isSuccess": True,
            "totalRecords": len(list_result),
            "data": jsonable_encoder(list_result),
        }
    )


@app.post("/face-api/search-face")
async def search_face(image: UploadFile = File(...), tableName: str = Form(...)):
    log.debug("Calling search_faces.")

    image_bytes = await image.read()

    nparr = np.frombuffer(image_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    session = Session()

    fa_faces = await analyze_image(img_np, fa, False)

    result = []

    for inp_face in fa_faces:
        fa_emb_str = str(json.dumps(inp_face.Embedding.tolist()))
        emb = "cube(ARRAY" + fa_emb_str + ")"

        query = text(
            "SELECT sub.* "
            "FROM "
            "( "
            "SELECT "
            + '"ImageID", '
            + '"ImageDetectID", '
            + '"ImageDetectPath", '
            + '"FaceDetectID", '
            + '"FaceDetectPath", '
            + '(1-(POWER(( "Embedding" <-> '
            + emb
            + " ),2)/2))*100 AS Similarity "
            f'FROM public."{tableName}" '
            ") AS sub "
            "WHERE sub.Similarity > 50 "
            "ORDER BY sub.Similarity DESC;"
        )

        query_res = session.execute(query)

        rows_proxy = query_res.fetchall()

        dict = {}

        for row_proxy in rows_proxy:
            for column, value in row_proxy.items():
                dict = {**dict, **{column: value}}
            if dict:
                dict["ImageSearchDetect"] = inp_face.ImageDetectPath
            result.append(dict)

    session.close()
    return JSONResponse(
        content={
            "isSuccess": True,
            "totalRecords": len(result),
            "data": jsonable_encoder(result),
        }
    )
