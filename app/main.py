import secrets
from flask import Flask, redirect, request, session, render_template
import os
import requests

app = Flask(__name__)

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URL = os.environ["REDIRECT_URL"]
app.secret_key = os.environ["SECRET_KEY"]


@app.route("/")
def index():
    return render_template("index.html")


# (no PKCE, manual impl)
@app.route("/login/")
def login():
    state = secrets.token_urlsafe(16)
    session["state"] = state
    return redirect(
        f"https://vlab.ustc.edu.cn/o/authorize/?response_type=code&client_id={CLIENT_ID}&redirect_url={REDIRECT_URL}&state={state}"
    )


@app.route("/callback/")
def callback():
    state = request.args.get("state", "")
    code = request.args.get("code", "")
    error = request.args.get("error", "")
    if session.get("state") is None or state != session["state"]:
        return "Inconsistent state value! Please re-login.", 401
    if error:
        return "Remote error: " + error, 401
    resp = requests.post(
        "https://vlab.ustc.edu.cn/o/token/",
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    )
    if resp.status_code != 200:
        print(resp.content, resp.status_code)
        return f"Get {resp.status_code} when trying to get token", 500
    resp = resp.json()
    access_token = resp["access_token"]  # default available for 1 hour
    scope = resp["scope"]  # currently, only "userinfo-basic" is available
    refresh_token = resp["refresh_token"]

    # Here we will go fetching userinfo directly -- you could also store access_token and refresh_token in your database
    resp = requests.get(
        "https://vlab.ustc.edu.cn/vm/oapi/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp = resp.json()
    return f"Your GID: {resp['gid']}, Student ID (username): {resp['username']}"
