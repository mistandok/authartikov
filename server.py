#FastAPI application
import base64
import hmac
import hashlib
import binascii
import json

from typing import Optional

from fastapi import FastAPI, Form, Cookie, Body
from fastapi import responses
from fastapi.responses import Response


app = FastAPI()

SECREET_KEY = "34afd03e10a6652120317d73b547363f18e019ebad120b89c5793ef4c5ac86e8"
PASSWORD_SALT = 'f5855952f3d0142c1a050d93c4df0980b0562d79e28d44e59b2a4a68523616bf'

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
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()

    if not username:
        return Response(login_page, media_type="text/html")

    valid_username = get_username_from_signed_string(username)

    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key='username')
        return response

    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key='username')
        return response

    return Response(
        f"Привет, {users[valid_username]['name']}! <br />"
        f"Баланс: {users[valid_username]['balance']}",
         media_type="text/html"
        )

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

@app.post("/login")
def process_login_page(data: dict = Body(...)):
    username, password = data["username"], data["password"]
    user = users.get(username)
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