import json
import logging
import os

import coloredlogs
import jinja2
import redis
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_session import Session
from pymongo import MongoClient
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
users_collection = mongo_client["PyBot"]["users"]
server_collection = mongo_client["PyBot"]["servers"]


@app.route("/", methods=["GET"])
def index():
    if not session.get("theme_url"):
        session["theme_url"] = url_for("static", filename="CSS/cyborg.min.css")
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login():
    return redirect("/api/v1/login")


@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("You have been logged out!", "success")
    return redirect("/")


@app.route("/admin", methods=["GET"])
def admin():
    if session.get("is_admin"):
        return render_template("admin.html")
    else:
        return render_template("errors/404.html")


@app.route("/admin/users", methods=["GET"])
def admin_users():
    if session.get("is_admin"):
        # make a call to bot /api/users api endpoint and pass json response to template
        res = requests.get(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/users",
                           headers={"Token": json.dumps(session["oauth2_token"])})
        if res.status_code == 200:
            return render_template("admin_users.html", users=json.loads(res.content.decode('utf8')))
        else:
            logger.debug(res.status_code)
            return "invalid response code!", 500
    else:
        return render_template("errors/404.html")


@app.route("/admin/servers", methods=["GET"])
def admin_servers():
    if session.get("is_admin"):
        # make a call to bot /api/servers api endpoint and pass json response to template
        res = requests.get(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/servers",
                           headers={"Token": json.dumps(session["oauth2_token"])})
        if res.status_code == 200:
            return render_template("admin_servers.html", servers=json.loads(res.content.decode('utf8')))
        else:
            return "invalid response code!", 500
    else:
        return render_template("errors/404.html")


@app.route("/admin/modules", methods=["GET"])
def admin_modules():
    if session.get("is_admin"):
        res = requests.get(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/modules",
                           headers={"Token": json.dumps(session["oauth2_token"])})
        if res.status_code == 200:
            return render_template("admin_modules.html", modules=json.loads(res.content.decode('utf8'))["modules"])
        else:
            return "invalid response code!", 500
    else:
        return render_template("errors/404.html")


@app.route("/api/v1/admin/banUser", methods=["POST"])
def admin_ban_user():
    if session.get("is_admin"):
        if request.is_json:
            user_id = request.get_json()["user_id"]
            user = users_collection.find_one({"id": int(user_id)})
            if user is not None:
                # user exists
                reason = request.get_json()["reason"]
                user["MiscData"]["is_banned"] = True
                users_collection.update_one({"id": int(user_id)}, {"$set": {"MiscData": user["MiscData"]}})

                res = requests.post(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/banUserNotification",
                                    json={"user_id": user_id, "reason": reason},
                                    headers={"Token": json.dumps(session["oauth2_token"])})
                logger.debug(
                    f"Response Code: {res.status_code}; Response Text: {res.text}; Response Content: {res.content}")
                if res.status_code == 200:
                    logger.debug("200 status")
                else:
                    logger.critical(f"Failed to send notification!")

                flash("User has been banned", "info")
                return "", 200
            else:
                flash("User was not found!", "error")
                return "user not found!", 400
        else:
            flash("Invalid Request!", "error")
            return "request is not json!", 400
    else:
        return "", 401


@app.route("/api/v1/admin/unbanUser", methods=["POST"])
def admin_unban_user():
    if session.get("is_admin"):
        if request.is_json:
            user_id = request.get_json()["user_id"]
            user = users_collection.find_one({"id": int(user_id)})
            if user is not None:
                # user exists
                user["MiscData"]["is_banned"] = False
                users_collection.update_one({"id": int(user_id)}, {"$set": {"MiscData": user["MiscData"]}})

                res = requests.post(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/unbanUserNotification",
                                    json={"user_id": user_id},
                                    headers={"Token": json.dumps(session["oauth2_token"])})
                logger.debug(
                    f"Response Code: {res.status_code}; Response Text: {res.text}; Response Content: {res.content}")
                if res.status_code == 200:
                    logger.debug("200 status")
                else:
                    logger.critical(f"Failed to send notification!")

                flash("User has been unbanned", "info")
                return "", 200
            else:
                flash("User was not found!", "error")
                return "user not found!", 400
        else:
            flash("Invalid Request!", "error")
            return "request is not json!", 400
    else:
        return "", 401


@app.route("/api/v1/admin/banServer", methods=["POST"])
def admin_ban_server():
    if session.get("is_admin"):
        if request.is_json:
            req_json = request.get_json()
            server_id = req_json["server_id"]
            server = server_collection.find_one({"id": int(server_id)})
            if server is not None:
                # server exists
                reason = req_json["reason"]
                server["settings"]["is_banned"] = True
                server_collection.update_one({"id": int(server_id)}, {"$set": {"settings": server["settings"]}})
                res = requests.post(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/banServerNotification",
                                    json={"server_id": server_id, "reason": reason},
                                    headers={"Token": json.dumps(session["oauth2_token"])})
                logger.debug(
                    f"Response Code: {res.status_code}; Response Text: {res.text}; Response Content: {res.content}")
                if res.status_code == 200:
                    logger.debug("200 status")
                else:
                    logger.critical(f"Failed to send notification!")

                flash("Server has been banned", "info")
                return "success", 200
            else:
                flash("Server was not found!", "error")
                return "server not found!", 400
        else:
            flash("Invalid Request!", "error")
            return "request is not json!", 400
    else:
        return "", 401


@app.route("/api/v1/admin/unbanServer", methods=["POST"])
def admin_unban_server():
    if session.get("is_admin"):
        if request.is_json:
            server_id = request.get_json()["server_id"]
            server = server_collection.find_one({"id": int(server_id)})
            if server is not None:
                # server exists
                server["settings"]["is_banned"] = False
                server_collection.update_one({"id": int(server_id)}, {"$set": {"settings": server["settings"]}})

                res = requests.post(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/unbanServerNotification",
                                    json={"server_id": server_id},
                                    headers={"Token": json.dumps(session["oauth2_token"])})
                logger.debug(
                    f"Response Code: {res.status_code}; Response Text: {res.text}; Response Content: {res.content}")
                if res.status_code == 200:
                    logger.debug("200 status")
                else:
                    logger.critical(f"Failed to send notification!")

                flash("Server has been unbanned", "info")
                return "success", 200
            else:
                flash("Server was not found!", "error")
                return "server not found!", 400
        else:
            flash("Invalid Request!", "error")
            return "request is not json!", 400
    else:
        return "", 401


@app.route("/api/v1/admin/leaveServer", methods=["POST"])
def admin_leave_server():
    if session.get("is_admin"):
        if request.is_json:
            server_id = request.get_json()["server_id"]
            res = requests.post(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/leaveServer",
                                json={"server_id": server_id}, headers={"Token": json.dumps(session["oauth2_token"])})
            logger.debug(
                f"Response Code: {res.status_code}; Response Text: {res.text}; Response Content: {res.content}")
            if res.status_code == 200:
                flash(res.text, "info")
                return "success", 200
            else:
                flash(res.text, "error")
            return "", res.status_code
        else:
            return "request is not json!", 400
    else:
        return "", 401


@app.route("/api/v1/login", methods=["GET"])
def login_redirect():
    discord = make_session(scope="identify email guilds")
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route("/api/v1/login/callback", methods=["GET"])
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
    flash(f"Welcome back, {session.get('user')['username']}!", "info")
    # check if the user id is in the admin DB
    result = admin_collection.find_one({"user_id": session.get("user")["id"]})
    if result is not None:
        session["is_admin"] = True
    else:
        session["is_admin"] = False
    return redirect(f"{BASE_URL}/dashboard")


@app.route("/manage/<int:guild_id>/overview", methods=["GET"])
def manage_server_overview(guild_id):
    # make api call to bot api to get specific guild by id and pass to template
    res = requests.get(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/server/{guild_id}",
                       headers={"Token": json.dumps(session["oauth2_token"])})
    if res.status_code != 200 and res.status_code == 400:
        return redirect(
            f"https://discordapp.com/api/oauth2/authorize?client_id=644927241855303691&permissions=8&scope=bot&guild_id={guild_id}")
    elif res.status_code != 200 and res.status_code != 400:
        return "invalid response!", 500
    else:
        return render_template("manage_overview.html", guild=json.loads(res.content))


@app.route("/manage/<int:guild_id>/modules", methods=["GET"])
def manage_server_modules(guild_id):
    # make api call to bot api to get specific guild by id and pass to template
    res = requests.get(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/server/{guild_id}",
                       headers={"Token": json.dumps(session["oauth2_token"])})
    if res.status_code != 200 and res.status_code == 400:
        return redirect(
            f"https://discordapp.com/api/oauth2/authorize?client_id=644927241855303691&permissions=8&scope=bot&guild_id={guild_id}")
    elif res.status_code != 200 and res.status_code != 400:
        return "invalid response!", 500
    else:
        modules_res = requests.get(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/server/{guild_id}/modules",
                                   headers={"Token": json.dumps(session["oauth2_token"])})
        if modules_res.status_code == 200:
            return render_template("manage_modules.html", guild=json.loads(res.content),
                                   modules=json.loads(modules_res.content))
        else:
            logger.critical(
                f"Failed to get modules for guild: {guild_id}; Response Code: {modules_res.status_code}; Response Text: {modules_res.text}")
            return "", modules_res.status_code


@app.route("/api/v1/<int:server_id>/toggleModule", methods=["POST"])
def toggle_server_module(server_id):
    if request.is_json:
        module = request.get_json()["module"]
        enabled = request.get_json()["enabled"]
        server = server_collection.find_one({"id": int(server_id)})
        if server is not None:
            # server exists
            server["settings"]["modules"][module] = bool(enabled)
            server_collection.update_one({"id": int(server_id)}, {"$set": {"settings": server["settings"]}})

            flash("Server modules updated", "info")
            return "success", 200
        else:
            flash("Server was not found!", "error")
            return "server not found!", 400
    else:
        flash("Invalid Request!", "error")
        return "request is not json!", 400


@app.route("/api/v1/admin/toggleModule", methods=["POST"])
def admin_toggle_module():
    if session.get("is_admin"):
        if request.is_json:
            module = request.get_json()["module"]
            enabled = request.get_json()["enabled"]
            res = requests.post(f"{os.getenv('BOT_API_BASE_URL')}/api/v1/admin/toggleModule",
                                json={"module": module, "enabled": enabled}, headers={"Token": json.dumps(session["oauth2_token"])})
            logger.debug(
                f"Response Code: {res.status_code}; Response Text: {res.text}; Response Content: {res.content}")
            if res.status_code == 200:
                flash(res.text, "info")
                return "success", 200
            else:
                flash(res.text, "error")
            return "", res.status_code
        else:
            flash("Invalid Request!", "error")
            return "request is not json!", 400
    else:
        return "", 401


@app.route("/api/v1/changeTheme", methods=["POST"])
def change_theme():
    if request.is_json:
        theme_name = request.get_json()["theme_name"]
        if theme_name == "bootstrap":
            session["theme_url"] = "https://bootswatch.com/_vendor/bootstrap/dist/css/bootstrap.min.css"
            flash("Theme Changed", "info")
            return "", 200
        else:
            session["theme_url"] = f"https://bootswatch.com/4/{theme_name}/bootstrap.min.css"
            flash("Theme Changed", "info")
            return "", 200
    else:
        return "request is not json!", 400


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
