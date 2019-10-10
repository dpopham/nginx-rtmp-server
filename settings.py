import os

TITLE="Darren's Stream Server"

SERVER_URL="https://tv.SOME_DOMAIN"

# Version of this app and client timer interval to check for changes
VERSION="0.4"
VERSION_INTERVAL=60

# dev parameters
DEBUG=False

# Listening Port
PORT=8000

# IP Address of nginx server - these are the IPs allowed to interact with app
NGINX_IPS=["WEB_SERVER_IP", "127.0.0.1"]

# Redis config
REDIS_SERVER="REDIS_SERVER_IP"

DOMAIN="SOME_DOMAIN"


# Location that nginx stores stream segments and keys
STREAM_FOLDER=os.path.dirname(os.path.realpath(__file__)) + '/streams'

#####################################################
# OAUTH Settings
# Provider
OAUTH_SERVER            = 'https://SOME_OAUTH_SERVER (in my case, Nextcloud server)'

# Main OAuth urls on your provider:
OAUTH_AUTHORIZATION_URL = '/apps/oauth2/authorize'    # OAuth Authorization URL
OAUTH_TOKEN_URL         = '/apps/oauth2/api/v1/token' # OAuth Access token URL

# The URL of some protected resource on your oauth2 server which you have configured to serve
# json-encoded user information (containing at least an email) for the user associated
# with a given access token.
OAUTH_RESOURCE_URL      = '/ocs/v2.php/cloud/user?format=json' # OAuth Resource URL

# From the configuration of your client site in the oauth2 provider
OAUTH_CLIENT_ID         = 'Client ID Stored on OAuth Server'
OAUTH_CLIENT_SECRET     = 'Super-secret secret stored on OAuth Server'
