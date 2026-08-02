import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading
import asyncio

# Discord Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE!')
    print(f'✅ Bot ID: {bot.user.id}')
    print(f'✅ Server count: {len(bot.guilds)}')
    
    # Sync commands
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
    await interaction.response.send_message(f'🔨 **{username}** banned! Reason: {reason}')

@bot.tree.command(name='kick', description='Kick a player from the game')
@app_commands.describe(username='Player username', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    await interaction.response.send_message(f'👢 **{username}** kicked! Reason: {reason}')

@bot.tree.command(name='info', description='Get player information')
@app_commands.describe(username='Player username')
async def info(interaction: discord.Interaction, username: str):
    embed = discord.Embed(title=f'📊 Player Info: {username}', color=0x00ff00)
    embed.add_field(name='🔨 Bans', value='0', inline=True)
    embed.add_field(name='✅ Status', value='Clean record', inline=True)
    await interaction.response.send_message(embed=embed)

# Flask webhook
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is running!'

@app.route('/webhook/exploit', methods=['POST'])
def exploit():
    data = request.json
    print(f'🚨 Exploit: {data}')
    return {'status': 'ok'}, 200

def run_flask():
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

# Start Flask in background
threading.Thread(target=run_flask, daemon=True).start()

# Run bot
bot.run(os.getenv('DISCORD_TOKEN'))
