import os
import flask
import requests
import pickle

import google.oauth2.credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from flask import Blueprint, redirect, url_for, flash, request

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://mail.google.com/']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

#extending flask app functionality
g_oauth = Blueprint('g_oauth', __name__)


# @param:   None
# @return:  Boolean
def authCheck():
    """
    Function that checks if token.pickle exists in the current directory for using to send emails and parse emails.
    If token.pickle exists then check if credits are valid,
    Else return False, which in the other function will require the user to Google Sing In with Bot credentials
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            return True

        else: return False

    return True

# @param:   credsreturn (True/False)
# @return:  redirect to Google Authentication
# @return:  creds (if credsreturn== True)
# @return:  None
def authLogin(credsreturn=False):
    """
    Function redirects to authorization if authCheck retured False.
    It also return credentials if needed
    """
    if not authCheck():
        return redirect('/authorizeService')

    if credsreturn:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            return creds

    return

# @param:   None
# @return:  service
def serviceBuilder():
    """
    Function creates an instance of gmail service.
    Function is used in emailRep to create the service to send emails.
    """

    creds = authLogin(credsreturn=True)
    service = build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)

    return service


#@param:    None
#@return:   redirect to authorization page
@g_oauth.route('/authorizeCheck')
def authorizeCheck():
    """
    "Check" function path
    Function that is used to redirect to Google Authentication Page

    For explanation about each code part refer to
    https://developers.google.com/identity/protocols/oauth2/web-server#example
    """

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = url_for('g_oauth.oauth2callbackCheck', _external=True, _scheme='https')

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return redirect(authorization_url)


#@param:    None
#@return:   redirect to authorization page
@g_oauth.route('/authorizeService')
def authorizeService():
    """
    "Check" function path
    Function that is used to redirect to Google Authentication Page

    For explanation about each code part refer to
    https://developers.google.com/identity/protocols/oauth2/web-server#example
    """

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('g_oauth.oauth2callbackService', _external=True, _scheme='https')

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    flask.session['state'] = state

    return redirect(authorization_url)

#@param:    None
#@return:   None
def oauth2callback():
    """
    Function that is used to receive authentication data and writes it to token.pickle
    """
    # Specify the state when creating the flow in the callback so that it can verified in the authorization server response.
    state = flask.session['state']

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('g_oauth.oauth2callbackCheck', _external=True,  _scheme='https')

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    if "http:" in authorization_response:
        authorization_response = "https:" + authorization_response[5:]
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials

    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    return

#@param:    None
#@return:   redirect to home page of web app
@g_oauth.route('/oauth2callbackCheck')
def oauth2callbackCheck():
    """
    Function that serves as oauth2callback.
    Redirect to the page to do the email verification after making token.pickle.
    """
    oauth2callback()
    flash('Authorized')
    return redirect('/')

#@param:    None
#@return:   serviceBuilder()
@g_oauth.route('/oauth2callbackService')
def oauth2callbackService():
    """
    Function that serves as oauth2callback.
    Goes back to building the service after making token.pickle.
    """
    oauth2callback()
    return serviceBuilder()