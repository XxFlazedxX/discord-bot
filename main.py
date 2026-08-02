import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading
import json

ALLOWED_USERS = [1376299488703938691, 1396417493475528774]
BAN_FILE = "bans.json"
PENDING_COMMANDS = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def load_bans():
    if not os.path.exists(BAN_FILE):
        return {}
    try:
        with open(BAN_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_bans(bans_dict):
    try:
        with open(BAN_FILE, 'w') as f:
            json.dump(bans_dict, f, indent=4)
        return True
    except:
        return False

def is_allowed(interaction):
    return interaction.user.id in ALLOWED_USERS

def is_user_banned(username):
    bans = load_bans()
    return username.lower() in bans

def add_ban_to_list(username, reason):
    bans = load_bans()
    bans[username.lower()] = {
        "reason": reason,
        "banned_at": "now"
    }
    return save_bans(bans)

def remove_ban_from_list(username):
    bans = load_bans()
    if username.lower() in bans:
        del bans[username.lower()]
        return save_bans(bans)
    return False

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE!')
    try:
        await bot.tree.sync()
        print('✅ Commands synced!')
    except Exception as e:
        print(f'❌ Error: {e}')

@bot.tree.command(name='ban', description='Permanently ban a player')
@app_commands.describe(username='Player username', reason='Ban reason')
async def ban(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if is_user_banned(username):
        return await interaction.response.send_message(f'⚠️ **{username}** is already banned!')
    
    if add_ban_to_list(username, reason):
        PENDING_COMMANDS.append({"command": "ban", "username": username, "reason": reason})
        await interaction.response.send_message(f'🔨 **{username}** permanently banned!\n📝 Reason: {reason}')
    else:
        await interaction.response.send_message('❌ Failed to save ban.')

@bot.tree.command(name='unban', description='Unban a player')
@app_commands.describe(username='Player username')
async def unban(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if not is_user_banned(username):
        return await interaction.response.send_message(f'⚠️ **{username}** is not banned.')
    
    if remove_ban_from_list(username):
        PENDING_COMMANDS.append({"command": "unban", "username": username})
        await interaction.response.send_message(f'✅ **{username}** unbanned!')
    else:
        await interaction.response.send_message('❌ Failed to unban.')

@bot.tree.command(name='kick', description='Kick a player')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    PENDING_COMMANDS.append({"command": "kick", "username": username, "reason": reason})
    await interaction.response.send_message(f'👢 **{username}** kicked!\n📝 Reason: {reason}')

@bot.tree.command(name='info', description='Get player info')
@app_commands.describe(username='Player username')
async def info(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    banned = is_user_banned(username)
    bans = load_bans()
    reason = bans.get(username.lower(), {}).get("reason", "N/A") if banned else "Not banned"
    
    embed = discord.Embed(title=f'📊 Player Info: {username}', color=0x00ff00)
    embed.add_field(name='🔨 Banned', value='✅ Yes' if banned else '❌ No', inline=True)
    embed.add_field(name='📝 Reason', value=reason, inline=False)
    await interaction.response.send_message(embed=embed)

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is running!'

@app.route('/roblox/pending', methods=['GET'])
def pending():
    if PENDING_COMMANDS:
        cmd = PENDING_COMMANDS.pop(0)
        return jsonify(cmd)
    return jsonify({'command': 'none'})

@app.route('/roblox/checkban/<username>', methods=['GET'])
def checkban(username):
    banned = is_user_banned(username)
    return jsonify({'banned': 'true' if banned else 'false'})

@app.route('/roblox/execute/<int:record_id>', methods=['POST'])
def execute_command(record_id):
    return jsonify({'status': 'ok'}), 200

def run_flask():
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
