import jinja2
import os
import logging
import coloredlogs
import redis
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, jsonify, redirect, flash
from flask_session import Session
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.debug = True

# load dotenv
load_dotenv()

# host
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = os.getenv("FLASK_PORT", 5000)

# load base url
BASE_URL = os.getenv("BASE_URL", "127.0.0.1:5000")

# load API Version
API_VERSION = os.getenv("API_VERSION", "v1")

# load env variables
OAUTH2_CLIENT_ID = os.getenv("CLIENT_ID", "")
OAUTH2_CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

# load redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# load redis for sessions
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)

# init session
app.config['SESSION_TYPE'] = 'redis'
app.config["SESSION_REDIS"] = redis_client
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
sess = Session()

# get logger
logger = logging.getLogger(__name__)

# URLS
REDIRECT_URI = f"{BASE_URL}/api/{API_VERSION}/login/callback"
AUTHORIZATION_BASE_URL = "https://discordapp.com/api/oauth2/authorize"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"
USER_URL = "https://discordapp.com/api/users/@me"
GUILDS_URL = "https://discordapp.com/api/users/@me/guilds"

# templates
TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

# init mongo client
mongo_client = MongoClient(os.getenv("MONGO_URI"))
admin_collection = mongo_client["PyBot"]["admins"]


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return redirect("/api/v1/login")


@app.route("/dashboard")
def dashboard():
    if session.get("user"):
        flash(f"Welcome, {session.get('user')['username']}!", "success")
        # check if the user id is in the admin DB
        result = admin_collection.find_one({"user_id": session.get("user")["id"]})
        if result is not None:
            session["is_admin"] = True
        else:
            session["is_admin"] = False
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect("/")


@app.route("/admin")
def admin():
    if session.get("is_admin"):
        return render_template("admin.html")
    else:
        return render_template("errors/404.html")


@app.route("/admin/users")
def admin_users():
    if session.get("is_admin"):
        # make a call to /api/v1/bot/users and store json list result in session
        pass
    else:
        return render_template("errors/404.html")


@app.route("/admin/servers")
def admin_servers():
    if session.get("is_admin"):
        # make a call to /api/v1/bot/servers and store json list result in session
        return render_template("admin_servers.html")
    else:
        return render_template("errors/404.html")


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
        flash("Error occurred!", "error")
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
    print("")
    print(user)
    print("")
    print(guilds)
    print("")
    return redirect(f"{BASE_URL}/dashboard")


@app.route("/api/v1/bot/servers")
async def api_servers():
    pass


@app.route("/api/v1/bot/users")
async def api_users():
    pass


@app.route("/manage/<int:guild_id>")
def manage_server(guild_id):
    return render_template("manage.html", guild_id=guild_id)


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
    app.run(host=FLASK_HOST, port=FLASK_PORT)
