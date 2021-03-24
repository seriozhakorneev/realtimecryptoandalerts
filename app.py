from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import uvicorn

from random import randint
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get('/data')
def data():
    return {
        'result' : datetime.now().strftime("%H:%M:%S"),
        'num10' : randint(1,11),
        'num100' : randint(1,101),
        }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app:app")