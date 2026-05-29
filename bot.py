import discord
import anthropic
from gtts import gTTS
import os
import asyncio

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_KEY"]
PREFIXO = "!"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

historico = []

PERSONALIDADE = "Você é o Pi, um membro e moderador do servidor, sociável, respeitoso mas bem zoeiro. De vez em quando chama as pessoas carinhosamente de 'lindo', 'meu bem', 'mozão', mas não o tempo todo. Usa gírias brasileiras naturalmente como 'pprt', 'baitola', 'mano', 'véi'. Fala curto e informal como em uma call com amigos. Mas quando alguém toca em filosofia ou matemática, fica sério e fala com profundidade sobre o assunto. Depois volta a ser zoeiro normalmente."

async def perguntar_claude(pergunta):
    historico.append({"role": "user", "content": pergunta})
    resposta = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=PERSONALIDADE,
        messages=historico
    )
    texto = resposta.content[0].text
    historico.append({"role": "assistant", "content": texto})
    return texto

@client.event
async def on_ready():
    print(f"Bot online como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # !entrar — bot entra na call
    if message.content == f"{PREFIXO}entrar":
        if message.author.voice:
            canal = message.author.voice.channel
            await canal.connect()
            await message.channel.send("Entrei na call! 🎙️")
        else:
            await message.channel.send("Você precisa estar em uma call primeiro!")

    # !sair — bot sai da call
    elif message.content == f"{PREFIXO}sair":
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send("Saí da call!")

    # !falar — responde só no texto
    elif message.content.startswith(f"{PREFIXO}falar "):
        pergunta = message.content[len(f"{PREFIXO}falar "):]
        texto = await perguntar_claude(pergunta)
        await message.channel.send(f"🤖 {texto}")

    # !voz — responde só na call
    elif message.content.startswith(f"{PREFIXO}voz "):
        pergunta = message.content[len(f"{PREFIXO}voz "):]
        vc = message.guild.voice_client
        if not vc:
            await message.channel.send("Me chama pra call primeiro com `!entrar`!")
            return
        texto = await perguntar_claude(pergunta)
        tts = gTTS(text=texto, lang="pt")
        tts.save("resposta.mp3")
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio("resposta.mp3"))

client.run(DISCORD_TOKEN)
