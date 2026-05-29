import discord
from groq import Groq
from gtts import gTTS
import os

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GROQ_KEY = os.environ["GROQ_KEY"]
PREFIXO = "!"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
groq = Groq(api_key=GROQ_KEY)

historico = []

PERSONALIDADE = "Você é o Pi, um membro e moderador do servidor, sociável, respeitoso mas bem zoeiro. De vez em quando chama as pessoas carinhosamente de 'lindo', 'meu bem', 'mozão', mas não o tempo todo. Usa gírias brasileiras naturalmente como 'pprt', 'baitola', 'mano', 'véi'. Fala curto e informal como em uma call com amigos. Mas quando alguém toca em filosofia ou matemática, fica sério e fala com profundidade sobre o assunto. Depois volta a ser zoeiro normalmente."

async def perguntar_groq(pergunta):
    historico.append({"role": "user", "content": pergunta})
    resposta = groq.chat.completions.create(
        model="llama3-8b-8192",
        max_tokens=300,
        messages=[{"role": "system", "content": PERSONALIDADE}] + historico
    )
    texto = resposta.choices[0].message.content
    historico.append({"role": "assistant", "content": texto})
    return texto

@client.event
async def on_ready():
    print(f"Bot online como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"Mensagem recebida: {message.content}")

    if message.content == f"{PREFIXO}entrar":
        if message.author.voice:
            canal = message.author.voice.channel
            await canal.connect()
            await message.channel.send("Entrei na call! 🎙️")
        else:
            await message.channel.send("Você precisa estar em uma call primeiro!")

    elif message.content == f"{PREFIXO}sair":
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send("Saí da call!")

    elif message.content.startswith(f"{PREFIXO}pi "):
        pergunta = message.content[len(f"{PREFIXO}pi "):]
        print(f"Pergunta: {pergunta}")
        try:
            texto = await perguntar_groq(pergunta)
            print(f"Resposta: {texto}")
            await message.channel.send(f"🤖 {texto}")
        except Exception as e:
            print(f"ERRO: {e}")
            await message.channel.send(f"Erro: {e}")
        
    elif message.content.startswith(f"{PREFIXO}pivoz "):
        pergunta = message.content[len(f"{PREFIXO}pivoz "):]
        if not vc:
            await message.channel.send("Me chama pra call primeiro com `!entrar`!")
            return
        texto = await perguntar_groq(pergunta)
        tts = gTTS(text=texto, lang="pt")
        tts.save("resposta.mp3")
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio("resposta.mp3"))

client.run(DISCORD_TOKEN)
