import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask, request, jsonify
import threading

# Discord Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ONLINE!')
    try:
        await bot.tree.sync()
        print('✅ Commands synced!')
    except Exception as e:
        print(f'❌ Error: {e}')

@bot.tree.command(name='ban', description='Ban a player')
@app_commands.describe(username='Player name', reason='Ban reason')
async def ban(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    await interaction.response.send_message(f'🔨 {username} banned! Reason: {reason}')

@bot.tree.command(name='kick', description='Kick a player')
@app_commands.describe(username='Player name', reason='Kick reason')
async def kick(interaction: discord.Interaction, username: str, reason: str = "No reason"):
    await interaction.response.send_message(f'👢 {username} kicked! Reason: {reason}')

@bot.tree.command(name='info', description='Get player info')
@app_commands.describe(username='Player name')
async def info(interaction: discord.Interaction, username: str):
    await interaction.response.send_message(f'📊 {username} - No bans found')

# Flask webhook
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is running!'

@app.route('/webhook/exploit', methods=['POST'])
def exploit():
    return {'status': 'ok'}, 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))

threading.Thread(target=run_flask, daemon=True).start()
bot.run(os.getenv('DISCORD_TOKEN'))
