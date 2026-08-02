import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading
import requests

ALLOWED_USERS = [1376299488703938691, 1396417493475528774]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def is_allowed(interaction):
    return interaction.user.id in ALLOWED_USERS

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE!')
    try:
        await bot.tree.sync()
        print('✅ Commands synced!')
    except Exception as e:
        print(f'❌ Error: {e}')

@bot.tree.command(name='ban', description='Ban a player')
@app_commands.describe(username='Player username', reason='Ban reason')
async def ban(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    # Send to Roblox via HTTP
    try:
        response = requests.post(
            'http://YOUR_ROBLOX_GAME_IP:PORT/ban',
            json={'username': username, 'reason': reason},
            timeout=2
        )
        await interaction.response.send_message(f'🔨 **{username}** banned! Reason: {reason}')
    except:
        await interaction.response.send_message(f'⚠️ Ban command sent but Roblox server not responding.')

@bot.tree.command(name='unban', description='Unban a player')
@app_commands.describe(username='Player username')
async def unban(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    try:
        response = requests.post(
            'http://YOUR_ROBLOX_GAME_IP:PORT/unban',
            json={'username': username},
            timeout=2
        )
        await interaction.response.send_message(f'✅ **{username}** unbanned!')
    except:
        await interaction.response.send_message(f'⚠️ Unban command sent but Roblox server not responding.')

@bot.tree.command(name='kick', description='Kick a player')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    
    try:
        response = requests.post(
            'http://YOUR_ROBLOX_GAME_IP:PORT/kick',
            json={'username': username, 'reason': reason},
            timeout=2
        )
        await interaction.response.send_message(f'👢 **{username}** kicked! Reason: {reason}')
    except:
        await interaction.response.send_message(f'⚠️ Kick command sent but Roblox server not responding.')

@bot.tree.command(name='info', description='Get player info')
@app_commands.describe(username='Player username')
async def info(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    embed = discord.Embed(title=f'📊 Player Info: {username}', color=0x00ff00)
    embed.add_field(name='🔨 Bans', value='0', inline=True)
    embed.add_field(name='✅ Status', value='Clean record', inline=True)
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
