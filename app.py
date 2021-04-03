from fastapi import FastAPI, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_utils.tasks import repeat_every
from fastapi.staticfiles import StaticFiles


from ast import literal_eval 
import uvicorn
import api


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
@repeat_every(seconds=1)
def make_api_request_and_save_tokens():
    try:
        api.write_json_file()
    except Exception:
        pass


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    session_pairs_list = []
    p_names = []
    pairs = await api.read_json_file()

    if pairs:
        # list of all pair names for <datalist/>
        p_names = pairs.keys()

    session_pairs = request.cookies.get('pairs')
    if session_pairs:
        # from str to list
        session_pairs_list = session_pairs.split(" ")
       
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session_pairs_list": session_pairs_list,
        "p_names": p_names,
        })


@app.get('/crt')
async def crt(response: Response):

    alerts = {'BTCUSDT' : 15}
    response.set_cookie(key="alerts", value=str(alerts)) 
    
    return 'success'

@app.get('/add_alert')
async def add_alert(request: Request, response: Response):

    alert_pair = 'BNBUSDT'
    alert_price = 17

    alerts = request.cookies.get('alerts')
    if alerts:
        # str to dict
        alerts_dict = literal_eval(alerts)
        alerts_dict[alert_pair] = alert_price

    # dict to str
    response.set_cookie(key="alerts", value=str(alerts_dict))

    return alerts_dict

@app.get('/get_alert')
async def get_alert(request: Request, response: Response):

    alerts = request.cookies.get('alerts')
    if alerts:
        # str to dict
        alerts_dict = literal_eval(alerts)

    return alerts_dict


@app.get('/data')
async def data(request: Request):
    result = []
    raise_alert = [None]
    pairs = await api.read_json_file()
    session_pairs = request.cookies.get('pairs')

    if session_pairs and pairs:
        session_pairs_list = session_pairs.split(" ")
        # get pairs prices
        for s_pair in session_pairs_list:
            price = pairs.get(s_pair)
            # если цена совпадает с алертом то
            # raise_alert = s_pair, alert
            result.append(price)

    #raise_alert = 'BTCUSDT', '0.0086739'
    return {
         'result': result,
         'raise_alert': raise_alert,
         }


@app.post("/add_pair")
async def add_pair(request: Request, trade_pair: str = Form(...)):
    
    session_pairs = request.cookies.get('pairs')
    if session_pairs:
        # from str to list
        session_pairs_list = session_pairs.split(" ")
        # add if already not in list
        if trade_pair not in session_pairs_list:
            # add new pair
            session_pairs_list.append(trade_pair)
    else:
        # create new if cookie empty
        session_pairs_list = [trade_pair]

     # redirect to index, and set new cookie
    redirect_resp = RedirectResponse('/', status_code=303)
    session_pairs_string = ' '.join(session_pairs_list)
    redirect_resp.set_cookie(key="pairs", value=session_pairs_string)

    return redirect_resp


@app.post("/delete_pair")
async def delete_pair(request: Request, trade_pair: str = Form(...)):
    
    session_pairs = request.cookies.get('pairs')
    if session_pairs:
        session_pairs_list = session_pairs.split(" ")
        # delete pair
        session_pairs_list.remove(trade_pair)

        # redirect to index, and set new cookie
        redirect_resp = RedirectResponse('/', status_code=303)
        session_pairs_string = ' '.join(session_pairs_list)
        redirect_resp.set_cookie(key="pairs", value=session_pairs_string)

    return redirect_resp


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)# reload=True


# how much cookie i can put in key
"""abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghi
jklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrst
uvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdef
ghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqr
stuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcde
fghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrs
tuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghi
jklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxy
zabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopq
rstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij
klmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcd
efghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvw
xyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuv
wxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvw
xyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcd
efghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij
klmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqr
stuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyza
bcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijkl
mnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvw
xyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij
klmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvw
xyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijk
lmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnop
qrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefgh
ijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyza
bcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstu
vwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnop
qrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijkl
mnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij
klmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefgh
ijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefg
hijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefg
hijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefgh
ijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijk
lmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmn
opqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqr
stuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvw
xyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzab
cdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefgh
ijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmno
pqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvw
xyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmn
"""