
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
import os, sys

from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run
from src.exception import CustomException
from src.logger import logging

from src.pipeline.predict_pipeline import  PredictionPipeline
from src.pipeline.train_pipeline import TrainPipeline

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/", tags=["authentication"])
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "context": "Rendering"}
    )


@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()

        train_pipeline.run_pipeline()

        return Response("Training successful !!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")



@app.post("/predict")
def predict(file: UploadFile = File(...)):
    try:
        pred_pipeline = PredictionPipeline(file)
        prediction_file = pred_pipeline.run_pipeline()
        file_location = prediction_file.prediction_file_path
        file_name = prediction_file.prediction_file_name
        logging.info("prediction finished")
        return FileResponse(file_location, media_type='application/octet-stream',filename=file_name)

    except Exception as e:
        raise CustomException(e,sys)

if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8080)
