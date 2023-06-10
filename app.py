from flask import Flask, request, redirect, session, render_template, url_for
from requests_oauthlib import OAuth2Session
import requests
import config
import bot
app = Flask(__name__)
app.secret_key = config.app_secret_key
app.config['SESSION_COOKIE_NAME'] = 'discord_login'

DEBUG = True

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def login():
    if 'discord_token' not in session:
        discord = OAuth2Session(config.discord_client_id, redirect_uri=config.discord_redirect_uri, scope=config.discord_oauth2_scope)
        authorization_url, state = discord.authorization_url(config.discord_oauth2_authorize_url)
        session['oauth_state'] = state
        return redirect(authorization_url)
    return redirect('/select_guild')

@app.route('/callback')
def callback():
    discord = OAuth2Session(config.discord_client_id, redirect_uri=config.discord_redirect_uri, scope=config.discord_oauth2_scope, state=session['oauth_state'])
    token = discord.fetch_token(config.discord_oauth2_token_url, client_secret=config.discord_client_secret, authorization_response=request.url)
    session['discord_token'] = token

    return redirect('/select_guild')

@app.route('/select_guild')
def select_guild():
    if "discord_token" in session:
        headers = {'Authorization': f'Bearer {session["discord_token"]["access_token"]}'}
        guilds_response = requests.get(f'{config.discord_api_base_url}/users/@me/guilds', headers=headers)
        guilds = guilds_response.json()

        managed_guilds = [guild for guild in guilds if (guild.get('permissions', 0) & 32) == 32]
        print(guilds + managed_guilds)
        return render_template('select_guild.html', guilds=managed_guilds)
    return redirect('/login')

@app.route('/welcome/<int:guild_id>', methods=['GET'])
def welcome(guild_id):
    if "discord_token" in session:
        headers = {
            'Authorization': f'Bearer {session["discord_token"]["access_token"]}'
        }
        guilds_response = requests.get(f'{config.discord_api_base_url}/users/@me/guilds', headers=headers)
        guilds_data = guilds_response.json()
        guilds = [guild for guild in guilds_data if (guild.get('permissions', 0) & 32) == 32]
        guild = guilds[0]
        botheaders = {'Authorization': f'Bot {config.token}'}
        channels_response = requests.get(f'{config.discord_api_base_url}/guilds/{guild_id}/channels', headers=botheaders)
        channels = channels_response.json()
        print(channels)
        try:
            text_channels = [channel for channel in channels if channel['type'] == 0]
        except Exception as e:
            return f"The bot is not in your discord server."
        return render_template('edit_welcome.html', guild_id=guild_id, channels=text_channels)
    return redirect('/login')

@app.route('/api/welcome/<int:guild_id>', methods=['POST'])
async def save_welcome_message(guild_id):
    if 'discord_token' in session:
        channel_id = int(request.form['channel'])
        message = request.form['message']
        
        data = {"channelid": channel_id, "guild_id": guild_id, "message": message}
        try:
            await bot.save_welcome_message(data)
        except:
            print("e")
        return 'Welcome message has been successfully saved.'
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=DEBUG, ssl_context=('server.crt', 'server.key'))