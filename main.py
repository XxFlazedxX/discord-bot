import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading
import requests
import json

ALLOWED_USERS = [1376299488703938691, 1396417493475528774]

SUPABASE_URL = "https://tknncuwzbcvlzgqqdyuz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrbm5jdXd6YmN2bHpncXFkeXV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU2MzA0NjcsImV4cCI6MjEwMTIwNjQ2N30.Ey0DkwFQu32Rb4-rnvQxoCJZf7m8aor3cPhOGVHbowU"

PENDING_COMMANDS = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def is_allowed(interaction):
    return interaction.user.id in ALLOWED_USERS

def add_command_to_supabase(command, username, reason=""):
    url = f"{SUPABASE_URL}/rest/v1/commands"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "command": command,
        "username": username,
        "reason": reason,
        "executed": False
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201]
    except:
        return False

def add_ban_to_list(username, reason):
    url = f"{SUPABASE_URL}/rest/v1/bans"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "username": username.lower(),
        "reason": reason,
        "banned_at": "now"
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201]
    except:
        return False

def remove_ban_from_list(username):
    url = f"{SUPABASE_URL}/rest/v1/bans?username=eq.{username.lower()}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        response = requests.delete(url, headers=headers)
        return response.status_code == 200
    except:
        return False

def is_user_banned(username):
    url = f"{SUPABASE_URL}/rest/v1/bans?username=eq.{username.lower()}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return len(data) > 0
    except:
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
    
    if add_ban_to_list(username, reason) and add_command_to_supabase("ban", username, reason):
        await interaction.response.send_message(f'🔨 **{username}** permanently banned!\n📝 Reason: {reason}')
    else:
        await interaction.response.send_message('❌ Failed to ban.')

@bot.tree.command(name='unban', description='Unban a player')
@app_commands.describe(username='Player username')
async def unban(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if not is_user_banned(username):
        return await interaction.response.send_message(f'⚠️ **{username}** is not banned.')
    
    if remove_ban_from_list(username):
        await interaction.response.send_message(f'✅ **{username}** unbanned!')
    else:
        await interaction.response.send_message('❌ Failed to unban. Check logs.')

@bot.tree.command(name='kick', description='Kick a player')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if add_command_to_supabase("kick", username, reason):
        await interaction.response.send_message(f'👢 **{username}** kicked!\n📝 Reason: {reason}')
    else:
        await interaction.response.send_message('❌ Failed to kick.')

@bot.tree.command(name='info', description='Get player info')
@app_commands.describe(username='Player username')
async def info(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    banned = is_user_banned(username)
    embed = discord.Embed(title=f'📊 Player Info: {username}', color=0x00ff00)
    embed.add_field(name='🔨 Banned', value='✅ Yes' if banned else '❌ No', inline=True)
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
    return jsonify({'banned': banned})

@app.route('/roblox/execute/<int:record_id>', methods=['POST'])
def execute_command(record_id):
    url = f"{SUPABASE_URL}/rest/v1/commands?id=eq.{record_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    data = {"executed": True}
    try:
        response = requests.patch(url, headers=headers, json=data)
        return jsonify({'status': 'ok'}), 200
    except:
        return jsonify({'status': 'error'}), 500

def run_flask():
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
