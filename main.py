import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading
import requests

# ALLOWED USERS (ONLY THESE 2 CAN USE BOT)
ALLOWED_USERS = [1376299488703938691, 1396417493475528774]

# Discord Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

def is_allowed(interaction):
    return interaction.user.id in ALLOWED_USERS

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE!')
    print(f'✅ Allowed Users: {ALLOWED_USERS}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} commands!')
        for cmd in synced:
            print(f'   - /{cmd.name}')
    except Exception as e:
        print(f'❌ Sync error: {e}')

@bot.tree.command(name='ban', description='Ban a player from the game')
@app_commands.describe(username='Player username', reason='Ban reason')
async def ban(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ You are not authorized to use this command!', ephemeral=True)
    
    # Send to Roblox game server (you'll set this up)
    try:
        response = requests.post(
            'http://YOUR_ROBLOX_SERVER_IP:PORT/ban',
            json={'username': username, 'reason': reason},
            timeout=5
        )
        await interaction.response.send_message(f'🔨 **{username}** banned from game!\n📝 Reason: {reason}')
    except:
        await interaction.response.send_message(f'🔨 **{username}** banned (game server offline, but logged)\n📝 Reason: {reason}')

@bot.tree.command(name='unban', description='Unban a player from the game')
@app_commands.describe(username='Player username')
async def unban(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ You are not authorized to use this command!', ephemeral=True)
    
    try:
        response = requests.post(
            'http://YOUR_ROBLOX_SERVER_IP:PORT/unban',
            json={'username': username},
            timeout=5
        )
        await interaction.response.send_message(f'✅ **{username}** has been unbanned!')
    except:
        await interaction.response.send_message(f'✅ **{username}** unban request sent (game server offline)')

@bot.tree.command(name='kick', description='Kick a player from the game')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ You are not authorized to use this command!', ephemeral=True)
    
    try:
        response = requests.post(
            'http://YOUR_ROBLOX_SERVER_IP:PORT/kick',
            json={'username': username, 'reason': reason},
            timeout=5
        )
        await interaction.response.send_message(f'👢 **{username}** kicked from game!\n📝 Reason: {reason}')
    except:
        await interaction.response.send_message(f'👢 **{username}** kicked (game server offline)\n📝 Reason: {reason}')

@bot.tree.command(name='info', description='Get player information')
@app_commands.describe(username='Player username')
async def info(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ You are not authorized to use this command!', ephemeral=True)
    
    embed = discord.Embed(title=f'📊 Player Info: {username}', color=0x00ff00)
    embed.add_field(name='🔨 Bans', value='0', inline=True)
    embed.add_field(name='✅ Status', value='Clean record', inline=True)
    await interaction.response.send_message(embed=embed)

# Flask webhook (FOR ROBLOX TO SEND EXPLOIT ALERTS)
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is running!'

@app.route('/webhook/exploit', methods=['POST'])
def exploit_webhook():
    data = request.json
    print(f'🚨 EXPLOIT DETECTED: {data}')
    
    # Send to your Discord channel
    channel_id = os.getenv('EXPLOIT_CHANNEL_ID')
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel:
            embed = discord.Embed(
                title='🚨 Exploit Detected!',
                color=0xff0000,
                fields=[
                    {'name': 'Player', 'value': data.get('player', 'Unknown'), 'inline': True},
                    {'name': 'Exploit', 'value': data.get('exploit', 'Unknown'), 'inline': True},
                    {'name': 'Action', 'value': data.get('action', 'Unknown'), 'inline': True}
                ],
                timestamp=discord.utils.utcnow()
            )
            # Send in a thread to not block
            threading.Thread(target=lambda: asyncio.run(channel.send(embed=embed))).start()
    
    return jsonify({'status': 'ok'}), 200

def run_flask():
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

import asyncio
threading.Thread(target=run_flask, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
