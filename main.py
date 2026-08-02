import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading
import requests

ALLOWED_USERS = [1376299488703938691, 1396417493475528774]
PENDING_COMMANDS = []

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
    PENDING_COMMANDS.append({'command': 'ban', 'username': username, 'reason': reason})
    await interaction.response.send_message(f'🔨 **{username}** banned!\n📝 Reason: {reason}')

@bot.tree.command(name='unban', description='Unban a player')
@app_commands.describe(username='Player username')
async def unban(interaction: discord.Interaction, username: str):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    PENDING_COMMANDS.append({'command': 'unban', 'username': username})
    await interaction.response.send_message(f'✅ **{username}** unbanned!')

@bot.tree.command(name='kick', description='Kick a player')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    if not is_allowed(interaction):
        return await interaction.response.send_message('❌ Not authorized', ephemeral=True)
    PENDING_COMMANDS.append({'command': 'kick', 'username': username, 'reason': reason})
    await interaction.response.send_message(f'👢 **{username}** kicked!\n📝 Reason: {reason}')

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

@app.route('/roblox/pending', methods=['GET'])
def pending():
    if PENDING_COMMANDS:
        cmd = PENDING_COMMANDS.pop(0)
        return jsonify(cmd)
    return jsonify({'command': 'none'})

def run_flask():
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
