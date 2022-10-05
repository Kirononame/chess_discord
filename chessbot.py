import json
import logging
from enum import Enum

import discord
from discord.ext import commands

import chess
from chess import Move
import chess.svg

import cairosvg

token = ""

with open("token.json", "r") as f:
    token = json.load(f)
    token = token["token"]

class ChessState(Enum):
    IDLE = 1
    CHALLENGE = 2
    READY = 3
    PLAYING = 4



def svg_to_png_file(svgcode):
    
    svg_file = "images/chess.svg"
    png_file = "images/chess.png"

    with open(svg_file, "w") as f:
        f.write(svgcode)

    cairosvg.svg2png(url=svg_file, write_to=png_file)

    return png_file

def make_embed(png_file, player1, player2):
    file = discord.File(png_file, filename="chess.png")
    embed = discord.Embed(title='Chess', description=f"A game between {player1} and {player2}", color=0x077ff7)
    embed.set_image(url="attachment://chess.png")
    embed.add_field(name='How to Play:', value='$play uci', inline=False)
    embed.add_field(name=player1, value='White', inline=False)
    embed.add_field(name=player2, value='Black', inline=False)

    return file, embed


class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}~')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        self._last_member = member


class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.board = None
        self.chessstate = ChessState.IDLE

        self.player1 = None
        self.player2 = None

    @commands.command()
    async def challenge(self, ctx, *, member: discord.Member = None):
        """Make chess challenge"""

        if(self.chessstate == ChessState.IDLE):
            member = member or ctx.author
            self.player1 = member.display_name
            self.chessstate = ChessState.CHALLENGE

            await ctx.send(member.display_name + " have started a challenge to accept type $accept")
    
    @commands.command()
    async def accept(self, ctx, *, member: discord.Member = None):
        """Accept chess challenge"""

        if(self.chessstate == ChessState.CHALLENGE):
            member = member or ctx.author
            self.player2 = member.display_name
            self.chessstate = ChessState.READY

            await ctx.send(member.display_name + " have have accepted the challenge to start type $start")


    @commands.command()
    async def reset(self, ctx, *, member: discord.Member = None):
        """Reset chess state to idle"""

        self.chessstate = ChessState.IDLE
        self.board = None
        self.player1 = None
        self.player2 = None

        msg = await ctx.send("Game Stopped")

        await msg.add_reaction("😢")
        

    @commands.command()
    async def start(self, ctx, *, member: discord.Member = None):
        """Start chess match"""

        if(self.chessstate == ChessState.READY):
            self.chessstate = ChessState.PLAYING
            self.board = chess.Board()

            png_file = svg_to_png_file(chess.svg.board(self.board, size=900))
            file, embed = make_embed(png_file, self.player1, self.player2)

            button = discord.ui.Button(label="Offer a Draw", style=discord.ButtonStyle.green, emoji="🤝")
            button1 = discord.ui.Button(label="Resign", style=discord.ButtonStyle.grey, emoji="☠️")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button1)

            await ctx.send(file=file, embed=embed, view=view)
    
    
    
    @commands.command()
    async def play(self, ctx, arg, *, member: discord.Member = None):
        """Play a move"""

        if(self.chessstate == ChessState.PLAYING):
            uci = arg
            if Move.from_uci(uci) in self.board.legal_moves:

                self.board.push_uci(uci)

                png_file = svg_to_png_file(chess.svg.board(self.board, size=900))
                png_file = svg_to_png_file(chess.svg.board(self.board, size=900))
                file, embed = make_embed(png_file, self.player1, self.player2)

                button = discord.ui.Button(label="Offer a Draw", style=discord.ButtonStyle.green, emoji="🤝")
                button1 = discord.ui.Button(label="Resign", style=discord.ButtonStyle.grey, emoji="☠️")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button1)
                
                await ctx.send(file=file, embed=embed, view=view)
            
            else:
                await ctx.send("Not a legal move")
        

class Bot(commands.Bot):

    async def on_ready(self):
        print("Ready")
        await self.add_cog(Greetings(self))
        await self.add_cog(Chess(self))
        



intents = discord.Intents.default()
intents.message_content = True

client = Bot(command_prefix = '$', intents=intents)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

client.run(token, log_handler=handler)


