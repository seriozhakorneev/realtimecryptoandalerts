from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi_utils.tasks import repeat_every

import uvicorn

from random import randint
from datetime import datetime
import api

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# httponly - 
# A bool indicating that the cookie cannot be accessed 
# via JavaScript through Document.cookie property,
#  the XMLHttpRequest or Request APIs. Optional

async def get_time():
    return datetime.now().strftime("%H:%M:%S")

async def get_10():
    return randint(1,11)

#@app.on_event("startup")
#@repeat_every(seconds=60 * 60)  # 1 hour
#def remove_expired_tokens_task() -> None:
 #   with sessionmaker.context_session() as db:
  #      remove_expired_tokens(db=db)

@app.on_event("startup")
@repeat_every(seconds=2)
def make_api_request_and_save_tokens():
    try:
        api.write_json_file()
    except Exception:
        pass

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    #tokens_list = []
    #tokens = request.cookies.get('tokens')
    #if tokens:
        # список который мы будем менять
        #tokens_list = tokens.split(" ")
        # список который мы будем возвращать в куки
        #tokens_string = ' '.join(tokens_list)
    
    
    return templates.TemplateResponse("index.html", {"request": request})



@app.get('/data')
async def data(): # bg_tasks: BackgroundTasks

    tokens = await api.read_json_file()
    result = None
    num10 = None
    num100  = None
    
    if tokens:
        for token in tokens:
            if token['symbol'] == 'BTCUSDT':
                result = f"{token['symbol']} : {token['price']}"

    #asyncio.sleep(1)
    #bg_tasks.add_task(api.write_json_file)

    return {
        'result' : result,
        'num10' : num10,
        'num100' : num100,
        }


@app.post("/create")
def create_cookie(response: Response):

    # создаю куки / пустой лист
    response.set_cookie(key="tokens", value="BTC ETH XLR")
    return {
        'cookies_created': response.headers["set-cookie"]
        }




@app.post("/delete")
def delete_cookie(response: Response):
    # создаю куки / пустой лист
    response.delete_cookie('tokens')
    return {
        response,
        #"response.headers": response.headers,
        
        }



if __name__ == "__main__":
    uvicorn.run("app:app")