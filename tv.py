"""
nginx secure streaming application
written by Darren Popham, 2019
"""

import os
import time
import datetime
import json

from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, abort
from flask import render_template
from flask.json import jsonify
from functools import wraps

# Redis for session storage
from redis import Redis
from redis_session import RedisSession, RedisSessionInterface

# Stream module to keep track of current streams
from streams import Streams

# Configuration settings
import settings


# Main Flask app
app = Flask(__name__)

# List of stream stored in Streams class
active_streams = Streams()

# Store session info in redis db
redis = Redis(settings.REDIS_SERVER)
app.session_interface = RedisSessionInterface(redis=redis,
                                              domain=settings.DOMAIN)


def valid_session():
    """ Retrieve session info from redis based upon stored cookie session id
        and then check if the OAuth info has expired.  If it is still valid
        then let user in since the presence of this OAuth key implies that
        the user has successfully logged in at some point. """
    if session is None or session.get('oauth_token', None) is None:
        app.logger.debug('INVALID Session: {}'.format(session))
        return False
    else:
        app.logger.debug('VALID Session: {}'.format(session))

        # it appears we have a valid session, but check if it has expired.....
        now = datetime.datetime.now().timestamp()
        expires_at = session.get('oauth_token', {}).get('expires_at', 0)

        # if token has expired refresh it
        if expires_at < now:
            app.logger.debug('but token has expired.... {}'.format(expires_at < now))
            token = session['oauth_token']
            extra = {
                'client_id': settings.OAUTH_CLIENT_ID,
                'client_secret': settings.OAUTH_CLIENT_SECRET,
            }

            # go fetch
            oauth_session = OAuth2Session(settings.OAUTH_CLIENT_ID, token=token)
            session['oauth_token'] = oauth_session.refresh_token(settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL, **extra)

            # Just a quick recheck in case something failed
            now = datetime.datetime.now().timestamp()
            expires_at = session.get('oauth_token', {}).get('expires_at', 0)
            if expires_at < now:
                app.logger.debug('Token refresh failed....')
                return False

        return True


def server_only(f):
    """ Decoration to limit access to nginx IPs only """
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Request must come from the NGINX_IPS list found in settings
        if request.remote_addr in settings.NGINX_IPS:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return wrapped


# Top level URL entry point
@app.route("/")
def default():
    return redirect(url_for('.home'))


# Begin login
@app.route("/login")
def login():
    """
    OAuth Start Login Flow
    Redirect the user/resource owner to the OAuth provider
    """
    # Just check for presence of access token
    if valid_session():
        app.logger.debug('Redirecting valid session to /home')
        return redirect(url_for('.home'))

    oauth_session = OAuth2Session(settings.OAUTH_CLIENT_ID)
    authorization_url, state = oauth_session.authorization_url(settings.OAUTH_SERVER + settings.OAUTH_AUTHORIZATION_URL)

    app.logger.info("URL: {}".format(authorization_url))

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Callback redirect provided to client by OAuth server
@app.route("/callback", methods=["GET"])
def callback():
    """
    OAuth Callback

    Client returns from OAuth provider with authorization code included.
    Use authorization code to obtain an access token from OAuth server.
    """

    # Check if session stored oauth state from initial login request
    if session.get('oauth_state', None) is None:
        return login()

    # Create session
    oauth_session = OAuth2Session(settings.OAUTH_CLIENT_ID,
                                  state=session['oauth_state'])


    # go fetch
    try:
        token = oauth_session.fetch_token(settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL,
                                          client_secret=settings.OAUTH_CLIENT_SECRET,
                                          authorization_response=request.url)
    except Exception as e:
        return login()

    # Save token in session (Redis)
    session['oauth_token'] = token

    # All good, send them home.....
    return redirect(url_for('.home'))


# Home
@app.route("/home", methods=["GET"])
def home():
    """
    Main page

    Pass parameters to the html page, such as title, version, timer interval to check
    for stream changes, etc., then render the page for the user.
    """
    return render_template('index.html',
                           button_text="Logout" if valid_session() else "Login to view Private Streams",
                           button_function="logout" if valid_session() else "login",
                           title="{} {}".format(settings.TITLE, "(Public Streams Only)" if not valid_session() else "(All Streams)"),
                           version=settings.VERSION,
                           interval=settings.VERSION_INTERVAL)


# Bye
@app.route("/logout", methods=["GET"])
def logout():
    """ Log user out of OAuth session """
    if valid_session():
        session['oauth_state'] = None
        session['oauth_token'] = None

    return redirect(url_for('.home'))


# Get list of streams
@app.route('/streams', methods=["GET"])
def streams():
    """  Return list of known streams to client.  If valid session, include encrypted streams """
    return jsonify(active_streams.check_streams(stream_type='all' if valid_session() else 'clear', server=settings.SERVER_URL))


# nginx call to verify user allowed to get key
@app.route("/authorize_key", methods=["GET"])
@server_only
def authorize_key():
    """ Called from nginx server to verify user has permission to access key """
    if valid_session():
        return 'OK'
    abort(401)


# screaching halt
@app.route("/stop_stream", methods=["POST"])
@server_only
def stop_stream():
    """ Called from nginx server when a stream stops.
        name is the 'key' used to identifiy the stream """
    if request is None or request.form is None or request.form.get('name', None) is None:
        abort(400)
    active_streams.check_streams()
    app.logger.debug('STOP STREAM: {}'.format(request.form.get('name')))
    return jsonify(success=True)


# giddy-up
@app.route("/start_stream", methods=["POST"])
@server_only
def start_stream():
    """ Called from nginx server when a new stream starts
        name is the 'key' used to identifiy the stream """
    if request is None or request.form is None or request.form.get('name', None) is None:
        abort(400)
    active_streams.check_streams()
    app.logger.debug('START STREAM: {}'.format(request.form.get('name')))
    return jsonify(success=True)


# giddy-up for all to see
@app.route("/start_clear_stream", methods=["POST"])
@server_only
def start_clear_stream():
    """ Called from nginx server when a new unencrypted stream starts
        name is the 'key' used to identifiy the stream """
    if request is None or request.form is None or request.form.get('name', None) is None:
        abort(400)
    active_streams.check_streams()
    app.logger.debug('START STREAM: {}'.format(request.form.get('name')))
    return jsonify(success=True)


# what version?
@app.route("/version", methods=["GET"])
def version():
    return jsonify(version=settings.VERSION)


# and so it begins......
if __name__ == "__main__":
    """ enable plain HTTP callback if needed """
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=settings.DEBUG, port=settings.PORT)

