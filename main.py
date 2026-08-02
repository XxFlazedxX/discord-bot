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

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def is_allowed(interaction):
    return interaction.user.id in ALLOWED_USERS

def add_command_to_supabase(command, username, reason=""):
    url = f"{SUPABASE_URL}/rest/v1/commands"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    data = {
        "command": command,
        "username": username,
        "reason": reason
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201]
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

@bot.tree.command(name='ban', description='Ban a player from the game')
@app_commands.describe(username='Player username', reason='Ban reason')
async def ban(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if add_command_to_supabase("ban", username, reason):
        await interaction.response.send_message(f'🔨 **{username}** banned!\n📝 Reason: {reason}')
    else:
        await interaction.response.send_message('❌ Failed to add ban to database.')

@bot.tree.command(name='unban', description='Unban a player from the game')
@app_commands.describe(username='Player username')
async def unban(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if add_command_to_supabase("unban", username):
        await interaction.response.send_message(f'✅ **{username}** unbanned!')
    else:
        await interaction.response.send_message('❌ Failed to add unban to database.')

@bot.tree.command(name='kick', description='Kick a player from the game')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    if add_command_to_supabase("kick", username, reason):
        await interaction.response.send_message(f'👢 **{username}** kicked!\n📝 Reason: {reason}')
    else:
        await interaction.response.send_message('❌ Failed to add kick to database.')

@bot.tree.command(name='info', description='Get player information')
@app_commands.describe(username='Player username')
async def info(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    url = f"{SUPABASE_URL}/rest/v1/commands?command=eq.ban&username=eq.{username}&select=count"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        ban_count = len(response.json()) if response.status_code == 200 else 0
    except:
        ban_count = 0
    
    embed = discord.Embed(title=f'📊 Player Info: {username}', color=0x00ff00)
    embed.add_field(name='🔨 Total Bans', value=str(ban_count), inline=True)
    embed.add_field(name='✅ Status', value='Clean record' if ban_count == 0 else 'Has bans', inline=True)
    await interaction.response.send_message(embed=embed)

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is running!'

@app.route('/webhook/exploit', methods=['POST'])
def exploit():
    data = request.json
    print(f'🚨 EXPLOIT: {data}')
    return jsonify({'status': 'ok'}), 200

def run_flask():
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
