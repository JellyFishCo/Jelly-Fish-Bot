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


@app.route('/home/<int:guild_id>')
def home(guild_id):
    if "discord_token" in session:
        botheaders = {'Authorization': f'Bot {config.dev_token}'}
        stuff = requests.get(f'{config.discord_api_base_url}/guilds/{guild_id}', headers=botheaders)
        guildresponse = stuff.json()
        return render_template("home.html", guild_id=guild_id, guildresponse=guildresponse)
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
        botheaders = {'Authorization': f'Bot {config.dev_token}'}
        channels_response = requests.get(f'{config.discord_api_base_url}/guilds/{guild_id}/channels', headers=botheaders)
        channels = channels_response.json()
        try:
            text_channels = [channel for channel in channels if channel['type'] == 0]
        except Exception as e:
            return f"The bot is not in your discord server."
        return render_template('edit_welcome.html', guild_id=guild_id, channels=text_channels)
    return redirect('/login')

@app.route('/verify/<int:guild_id>', methods=['GET'])
def verify(guild_id):
    if "discord_token" in session:
        headers = {
            'Authorization': f'Bearer {session["discord_token"]["access_token"]}'
        }
        guilds_response = requests.get(f'{config.discord_api_base_url}/users/@me/guilds', headers=headers)
        guilds_data = guilds_response.json()
        guilds = [guild for guild in guilds_data if (guild.get('permissions', 0) & 32) == 32]
        guild = guilds[0]
        botheaders = {'Authorization': f'Bot {config.dev_token}'}
        roles_response = requests.get(f'{config.discord_api_base_url}/guilds/{guild_id}/roles', headers=botheaders)
        roles = roles_response.json()
        channels_response = requests.get(f'{config.discord_api_base_url}/guilds/{guild_id}/channels', headers=botheaders)
        channels = channels_response.json()
        try:
            text_channels = [channel for channel in channels if channel['type'] == 0]
            actual_roles = [role for role in roles if role['name'] != "@everyone"]
        except Exception as e:
            return f"The bot is not in your discord server."
        return render_template('verify_setup.html', guild_id=guild_id, roles=actual_roles, channels=text_channels)
    return redirect('/login')

@app.route('/api/welcome/<int:guild_id>', methods=['POST'])
async def save_welcome_message(guild_id):
    if 'discord_token' in session:
        success_message = request.args.get('success_message')
        channel_id = int(request.form['channel'])
        message = request.form['message']
    
        data = {"channelid": channel_id, "guild_id": guild_id, "message": message}
        try:
            await bot.save_welcome_message(data, guild_id)
            success_message = "Welcome message updated successfully"
            return redirect(url_for('welcomesuccess', guild_id=guild_id))
        except:
            print("e")
        return redirect(url_for('welcome', guild_id=guild_id))
    return redirect('/login')

@app.route('/api/verify/<int:guild_id>', methods=['POST'])
async def save_verification(guild_id):
    if 'discord_token' in session:
        success_message = request.args.get('success_message')
        channel_id = int(request.form['channel'])
        role_id = int(request.form['role'])
        message = request.form['message']
    
        data = {"channelid": channel_id, "role_id": role_id, "guild_id": guild_id, "message": message}
        try:
            await bot.save_verification(data, guild_id)
            success_message = "Verification has been setup successfully"
            return redirect(url_for('verifysuccess', guild_id=guild_id))
        except Exception as e:
            print(e)
        return redirect(url_for('verify', guild_id=guild_id))
    return redirect('/login')


@app.route('/welcomesuccess/<int:guild_id>')
def welcomesuccess(guild_id):
    return redirect(url_for('home', guild_id=guild_id, success_message='Welcome message updated successfully.'))

@app.route('/verifysuccess/<int:guild_id>')
def verifysuccess(guild_id):
    return redirect(url_for('home', guild_id=guild_id, success_message='Verification has been setup successfully.'))


if __name__ == '__main__':
    app.run(debug=DEBUG, ssl_context=('server.crt', 'server.key'))