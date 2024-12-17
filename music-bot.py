import discord
from discord.ext import commands
import yt_dlp
import asyncio


intents = discord.Intents.default()
intents.message_content = True

#  prefix: 'ngawi play', 'ngawi join', dll
bot = commands.Bot(
    command_prefix=lambda bot, msg: msg.content.split()[0] + ' ' if msg.content.startswith("ngawi ") else None,
    intents=intents
)


queue = []


@bot.event
async def on_ready():
    print(f"Bot {bot.user} telah siap!")


async def play_song(ctx):
    if not queue:
        await ctx.send("Queue kosong. Tambahkan lagu dengan perintah `ngawi play <URL>`.")
        return

    url = queue.pop(0)  
    vc = ctx.voice_client 

    with yt_dlp.YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
        except Exception as e:
            await ctx.send(f"❌ Gagal memuat lagu: {e}")
            return

    ffmpeg_options = {
        'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }

    def after_play(error):
        if error:
            print(f"Error: {error}")
        else:
            bot.loop.create_task(play_song(ctx))

    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_play)
    await ctx.send(f"🎶 Sekarang memutar: {info['title']}")


@bot.command()
async def join(ctx):
    if ctx.author.voice: 
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"✅ Ngawitify telah bergabung di channel: {channel}")
    else:
        await ctx.send("❌ Anda harus berada di voice channel terlebih dahulu!")

@bot.command()
async def play(ctx, url: str):
    if not ctx.voice_client: 
        await ctx.invoke(join)

    queue.append(url) 
    await ctx.send(f"🎵 Lagu ditambahkan ke antrian: {url}")

    if not ctx.voice_client.is_playing(): 
        await play_song(ctx)


@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop() 
        await ctx.send("⏭ Lagu dilewati.")
    else:
        await ctx.send("❌ Tidak ada lagu yang sedang diputar.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client: 
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Ngawitify telah keluar dari voice channel.")
    else:
        await ctx.send("❌ Ngawitify tidak berada di voice channel.")

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000) 
    await ctx.send(f"🏓 Ping bot: {latency}ms")

bot.run("TOKEN")
