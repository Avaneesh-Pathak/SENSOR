from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

from src.pipeline.predict_pipeline import CustomData, PredictPipeline
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

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request

        self.gender: Optional[str] = None

        self.age: Optional[str] = None

        self.ethnicity: Optional[str] = None

        self.parental_level_of_education: Optional[str] = None

        self.lunch: Optional[str] = None

        self.test_preparation_course: Optional[str] = None

        self.writing_score: Optional[str] = None

        self.reading_score: Optional[str] = None

    async def get_data(self):
        form = await self.request.form()

        self.gender = form.get("gender")

        self.age = form.get("age")

        self.ethnicity = form.get("ethnicity")

        self.parental_level_of_education = form.get("parental_level_of_education")

        self.lunch = form.get("lunch")

        self.test_preparation_course = form.get("test_preparation_course")

        self.writing_score = form.get("writing_score")

        self.reading_score = form.get("reading_score")


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


@app.post("/")
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)

        await form.get_data()

        data = CustomData(
            gender=form.gender,
            race_ethnicity=form.ethnicity,
            parental_level_of_education=form.parental_level_of_education,
            lunch=form.lunch,
            test_preparation_course=form.test_preparation_course,
            reading_score=form.reading_score,
            writing_score=form.writing_score,
        )

        pred_df = data.get_data_as_data_frame()

        prediction_pipeline = PredictPipeline()

        preds = prediction_pipeline.predict(features=pred_df)

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "context": preds[0]},
        )

    except Exception as e:
        return Response(f"Error Occurred! {e}")


if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8080)
