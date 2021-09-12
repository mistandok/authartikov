#FastAPI application
import base64
import hmac
import hashlib
import binascii
import json

from decouple import config

from typing import Optional

from fastapi import FastAPI, Form, Cookie, Body, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECREET_KEY = config("SECREET_KEY")
PASSWORD_SALT = config("PASSWORD_SALT")


users = {
    "alexey@user.com": {
        "name": "Алексей",
        "password": "2ea2f64b06ec029c7aea0f44bc4d897b21fddd54d2363870ac13f809d59ffdb1",
        "balance": 100_000
    },
    "petr@user.com": {
        "name": "Петр",
        "password": "f102780e40fb4488243e8f958388abd04fce61c38e8bf63f5a2fa36856b39880",
        "balance": 555_555
    }
}


def sign_data(data: str) -> str:
    """return signed data"""
    return hmac.new(
        SECREET_KEY.encode(), 
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")

    try:
        username = base64.b64decode(username_base64.encode()).decode()
    except binascii.Error as err:
        username = ''

    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() ).hexdigest().lower()
    stored_password_hash = users[username]['password'].lower()
    return password_hash == stored_password_hash


@app.get("/")
def index_page(request: Request, username: Optional[str] = Cookie(default=None)):
    if not username:
        return templates.TemplateResponse("login.html", {"request": request})

    valid_username = get_username_from_signed_string(username)

    if not valid_username:
        response = templates.TemplateResponse("login.html", {"request": request})
        response.delete_cookie(key='username')
        return response

    try:
        user = users[valid_username]
    except KeyError:
        response = templates.TemplateResponse("login.html", {"request": request})
        response.delete_cookie(key='username')
        return response

    return Response(
        f"Привет, {users[valid_username]['name']}! <br />"
        f"Баланс: {users[valid_username]['balance']}",
         media_type="text/html"
        )


@app.post("/login")
def process_login_page(data: dict = Body(...)):
    username, password = data["username"], data["password"]
    user = users.get(username)
    print(f'Username {username}, Password {password}')
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                "success": False,
                "message": "Я вас не знаю!"
            }),
            media_type="application/json")
    
    response = Response(
        json.dumps({
            "success": True,
            "message": f"Привет, {user['name']}! <br />Баланс: {user['balance']}"
        })
        , media_type="text/html")
    username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response


# @app.post("/login")
# def process_login_page(username: str = Form(...), password: str = Form(...)):
#     user = users.get(username)
#     if not user or not verify_password(username, password):
#         return Response(
#             json.dumps({
#                 "success": False,
#                 "message": "Я вас не знаю!"
#             }),
#             media_type="application/json")
    
#     response = Response(
#         json.dumps({
#             "success": True,
#             "message": f"Привет, {user['name']}! <br />Баланс: {user['balance']}"
#         })
#         , media_type="text/html")
#     username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
#     response.set_cookie(key="username", value=username_signed)
#     return response