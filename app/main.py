from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.utils import run_topic_analysis, build_homepage_cards

import math

app = FastAPI(title="ViralBite API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/artifacts", StaticFiles(directory="app/artifacts"), name="artifacts")

templates = Jinja2Templates(directory="app/templates")


def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request}
    )


@app.get("/homepage")
def homepage():
    topics = [
        "nyc bagel",
        "matcha latte",
        "brooklyn pizza"
    ]
    result = build_homepage_cards(topics)
    return clean_nan(result)


@app.get("/analyze")
def analyze(query: str = Query(..., description="Topic to analyze")):
    result = run_topic_analysis(query)
    return clean_nan(result)