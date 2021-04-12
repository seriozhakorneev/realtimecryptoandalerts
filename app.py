from fastapi import FastAPI, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi_utils.tasks import repeat_every
from fastapi.staticfiles import StaticFiles

import uvicorn

from ast import literal_eval
import api

# config
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# functions
def control_cookie_size(cookie_string):
    # return True if cookies 
    # reached their limit(4kb)
    if cookie_string:
        return len(cookie_string.encode('utf-8')) > 4000

    return False

def check_alerts(alerts_dict, price, s_pair):
    # return alert and change alert_values
    alert_values = alerts_dict[s_pair]

    if (alert_values[0] != None) and (alert_values[0] <= float(price)):
        raise_alert = s_pair, alert_values[0]
        alerts_dict[s_pair][0] = None
        return raise_alert

    elif (alert_values[1] != None) and (alert_values[1] >= float(price)):
        raise_alert = s_pair, alert_values[1]
        alerts_dict[s_pair][1] = None
        return raise_alert

    return [None]

# routes
@app.on_event("startup")
@repeat_every(seconds=1)
def make_api_request_and_save_tokens():
    try:
        api.write_json_file()
    except Exception:
        pass


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # get cookies
    session_pairs = request.cookies.get('pairs')
    alerts = request.cookies.get('alerts')
    session_pairs_list = []
    alerts_dict = {}
    p_names = []
    # read prices file
    pairs = await api.read_json_file()
    
    if pairs:
        # list of all pair names for <datalist/>
        p_names = pairs.keys()
    if session_pairs:
        # str to list
        session_pairs_list = session_pairs.split(" ")
    if alerts:
        # str to dict
        alerts_dict = literal_eval(alerts)
       
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session_pairs_list": session_pairs_list,
        "alerts_dict": alerts_dict,
        "p_names": p_names,
        })


@app.get("/notes", response_class=HTMLResponse)
async def notes(request: Request):
    return templates.TemplateResponse("notes.html", {"request": request})

@app.get("/sw.js")
async def sw():
    return FileResponse('templates/sw.js', media_type='application/javascript')

@app.get('/data')
async def data(request: Request,response: Response,):
    result = []
    raise_alert = [None]
    pairs = await api.read_json_file()
    session_pairs = request.cookies.get('pairs')
    alerts = request.cookies.get('alerts')
    
    if session_pairs and pairs:
        session_pairs_list = session_pairs.split(" ")
        # get pairs prices
        for s_pair in session_pairs_list:
            price = pairs.get(s_pair)
            result.append(price)

            # alerts
            if alerts:
                alerts_dict = literal_eval(alerts)
                if s_pair in alerts_dict.keys():
                    raise_alert = check_alerts(alerts_dict, price, s_pair)

                    # if alert raised, change cookie
                    if raise_alert[0]:
                        # delete pair if no alerts left
                        if alerts_dict[s_pair].count(None) == 2:
                            del alerts_dict[s_pair]
                        # save to cookie
                        response.set_cookie(
                            key="alerts",
                            value=str(alerts_dict),
                            expires=1209600)
                            # 2 weeks in seconds
    #raise_alert = 'asd', '432'
    return {
         'result': result,
         'raise_alert': raise_alert,
         }


@app.post("/add_pair")
async def add_pair(request: Request, trade_pair: str = Form(...)):
    
    session_pairs = request.cookies.get('pairs')

    if control_cookie_size(session_pairs):
        return "Your cookies reached their limit of 4kb."

    if session_pairs:
        session_pairs_list = session_pairs.split(" ")
        # add if already not in list
        if trade_pair not in session_pairs_list:
            session_pairs_list.append(trade_pair)
    else:
        # create new if cookie empty
        session_pairs_list = [trade_pair]

     # redirect to index, and set new cookie
    redirect_resp = RedirectResponse('/', status_code=303)
    session_pairs_string = ' '.join(session_pairs_list)
    redirect_resp.set_cookie(key="pairs", value=session_pairs_string, expires=1209600)
    return redirect_resp


@app.post('/add_alert')
async def add_alert(
    request: Request,
    trade_pair: str = Form(...),
    alert_val: float = Form(...),
    direction: str = Form(...)):

    values = [None, None]
    alerts_dict = {}
    req_alerts = request.cookies.get('alerts')
    
    if control_cookie_size(req_alerts):
        return "Your cookies reached their limit of 4kb."

    # radiobutton index for values list
    if direction == "up":
        a_index = 0
    elif direction == "down":
        a_index = 1
    
    if req_alerts:
        alerts_dict = literal_eval(req_alerts)
        # if pair is in cookie
        current_values = alerts_dict.get(trade_pair)
        if current_values:
            values = current_values  

    values[a_index] = alert_val
    alerts_dict[trade_pair] = values

    redirect_resp = RedirectResponse('/', status_code=303)
    redirect_resp.set_cookie(key="alerts", value=str(alerts_dict), expires=1209600)
    return redirect_resp


@app.post("/delete_pair")
async def delete_pair(request: Request, trade_pair: str = Form(...)):
    
    session_pairs = request.cookies.get('pairs')
    redirect_resp = RedirectResponse('/', status_code=303)

    if session_pairs:
        session_pairs_list = session_pairs.split(" ")
        # delete pair
        session_pairs_list.remove(trade_pair)
        
        alerts = request.cookies.get('alerts')
        if alerts:
            alerts_dict = literal_eval(alerts)

            values = alerts_dict.get(trade_pair)
            if values:
                # delete alert pair 
                del alerts_dict[trade_pair]
            
                redirect_resp.set_cookie(
                    key="alerts",
                    value=str(alerts_dict),
                    expires=1209600)

        
        session_pairs_string = ' '.join(session_pairs_list)
        redirect_resp.set_cookie(key="pairs", value=session_pairs_string, expires=1209600)
        
    return redirect_resp


@app.post('/delete_alert')
async def delete_alert(
    request: Request,
    trade_pair: str = Form(...),
    alert_index: int = Form(...),):

    req_alerts = request.cookies.get('alerts')

    if req_alerts:
        alerts_dict = literal_eval(req_alerts)
        
        values = alerts_dict.get(trade_pair)
        if values:
            # delete alert
            values[alert_index] = None
            alerts_dict[trade_pair] = values
            
            # delete pair if no alerts left
            if values.count(None) == 2:
                del alerts_dict[trade_pair]
    
    redirect_resp = RedirectResponse('/', status_code=303)
    redirect_resp.set_cookie(key="alerts", value=str(alerts_dict), expires=1209600)
    return redirect_resp

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)# reload=True