import jinja2
import requests
import os
import logging
import coloredlogs
import redis
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, jsonify, redirect
from flask_session import Session
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.debug = True

# load dotenv
load_dotenv()

# load env variables
OAUTH2_CLIENT_ID = os.getenv("CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# load redis for sessions
redis_client = redis.Redis(host='185.230.160.118', port=6379, db=0) 

# ini session
app.config['SESSION_TYPE'] = 'redis'
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
sess = Session()

# get logger
logger = logging.getLogger(__name__)

# URLS
REDIRECT_URI = 'http://127.0.0.1:5000/api/v1/login/callback'
AUTHORIZATION_BASE_URL = "https://discordapp.com/api/oauth2/authorize"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"
USER_URL = "https://discordapp.com/api/users/@me"
GUILDS_URL = "https://discordapp.com/api/users/@me/guilds"

# templates
TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/api/v1/login")
def login_redirect():
    scopes = "identify email guilds"
    discord = make_session(scope=scopes)
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route("/api/v1/login/callback")
def login_callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    discord = make_session(token=token)
    user = discord.get(USER_URL).json()
    guilds = discord.get(GUILDS_URL).json()
    session["user"] = user
    session["guilds"] = guilds
    return redirect("http://127.0.0.1:5000/dashboard")


@app.errorhandler(400)
def bad_request(e):
    return render_template(TEMPLATES.get_template("errors/400.html")), 400


@app.errorhandler(401)
def unauthorized(e):
    return render_template(TEMPLATES.get_template("errors/401.html")), 401


@app.errorhandler(403)
def forbidden(e):
    return render_template(TEMPLATES.get_template("errors/403.html")), 403


@app.errorhandler(404)
def not_found(e):
    return render_template(TEMPLATES.get_template("errors/404.html")), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template(TEMPLATES.get_template("errors/500.html")), 500


@app.errorhandler(501)
def not_implemented(e):
    return render_template(TEMPLATES.get_template("errors/501.html")), 501


@app.errorhandler(502)
def bad_gateway(e):
    return render_template(TEMPLATES.get_template("errors/502.html")), 502


@app.errorhandler(503)
def service_unavailable(e):
    return render_template(TEMPLATES.get_template("errors/503.html")), 503


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


if __name__ == '__main__':
    # Init colored logger
    coloredlogs.install(logger=logger, level="DEBUG")

    # set env variable to allow HTTP redirect url
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Run
    app.run()
