from flask import Flask, request, redirect, session, render_template
from requests_oauthlib import OAuth1Session
import requests
import config
app = Flask(__name__)
app.secret_key = config.app_secret_key
app.config['SESSION_COOKIE_NAME'] = 'discord_login'

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def login():
    discord = OAuth1Session(config.discord_client_id, redirect_uri=config.discord_redirect_uri, scope=config.discord_oauth2_scope)
    authorization_url, state = discord.authorization_url(config.discord_oauth2_authorize_url)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    discord = OAuth1Session(config.discord_client_id, redirect_uri=config.discord_redirect_uri, scope=config.discord_oauth2_scope, state=session['oauth_state'])
    token = discord.fetch_token(config.discord_oauth2_token_url, client_secret=config.discord_client_secret, authorization_response=request.url)
    session['discord_token'] = token

    return redirect('/select_guild')

@app.route('/select_guild')
def select_guild():
    headers = {'Authorization': f'Bearer {session["discord_token"]["access_token"]}'}
    guilds_response = requests.get(f'{config.discord_api_base_url}/users/@me/guilds', headers=headers)
    guilds = guilds_response.json()

    managed_guilds = [guild for guild in guilds if guild["permissions"] == 0 & 32 == 32]

    return render_template('select_guild.html', guilds=managed_guilds)


@app.route('/welcome/<int:guild_id>', methods=['GET'])
def edit_welcome(guild_id):
    headers = {
        'Authorization': f'Bearer {session["discord_token"]["access_token"]}'
    }
    guilds_response = requests.get(f'{config.discord_api_base_url}/users/@me/guilds', headers=headers)
    guilds_data = guilds_response.json()
    guilds = [guild for guild in guilds if guild["permissions"] == 0 & 32 == 32]
    guild = guilds[0]
    channels_response = requests.get(f'{config.discord_api_base_url}/guilds/{guild["id"]}/channels', headers=headers)
    channels = channels_response.json()

    text_channels = [channel for channel in channels if channel['type'] == 0]

    return render_template('welcome.html', guild_id=guild_id, channels=text_channels)


if __name__ == '__main__':
    app.run(debug=True)