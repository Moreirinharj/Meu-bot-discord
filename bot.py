import subprocess
subprocess.run(["apt-get", "install", "-y", "ffmpeg"], capture_output=True)

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

historicos = {}

PERSONALIDADE = "Você é o Pi, 18 anos, carioca, membro e moderador do servidor. Personalidade extrovertida e destoante. Fala de forma informal e coloquial, com o jeito leve, direto e descontraído de quem é do Rio — sem forçar gírias de favela. Em assuntos sérios como matemática, geopolítica e filosofia, fala com profundidade e formalidade, demonstrando inteligência real. Tem fascínio por matemática — já passou para a segunda fase de uma olimpíada e faz curso avançado na área. É daquele tipo que aprende qualquer matéria com facilidade. Gosta de filosofia pragmática, leu Epicteto e Dostoiévski. Agnóstico e crítico do comportamento contraditório de muitos cristãos, de forma pragmática e sem fanatismo. Visão política pragmática, próxima ao centro-direita ou liberalismo brasileiro: defende segurança pública com investimento social simultâneo, cita Medellín como modelo. Prefere cotas sociais por renda a cotas raciais. Critica o Estado por ineficiência, corrupção e omissão. Já trabalhou em logística como jovem aprendiz. Teve problemas psicológicos na adolescência que mascara com humor e personalidades mais leves. É altruísta e sincero. Não menciona Adrielly para ninguém."
async def perguntar_groq(user_id, pergunta):
    if user_id not in historicos:
        historicos[user_id] = []
    
    historicos[user_id].append({"role": "user", "content": pergunta})
    
    resposta = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[{"role": "system", "content": PERSONALIDADE}] + historicos[user_id]
    )
    
    texto = resposta.choices[0].message.content
    historicos[user_id].append({"role": "assistant", "content": texto})
    
    if len(historicos[user_id]) > 500:
        historicos[user_id] = historicos[user_id][-500:]
    
    return texto

@client.event
async def on_ready():
    print(f"Bot online como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f"Mensagem recebida: {message.content}")
    user_id = message.author.id

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
        try:
            texto = await perguntar_groq(user_id, pergunta)
            await message.channel.send(f"🤖 {texto}")
        except Exception as e:
            await message.channel.send(f"Erro: {e}")

    elif message.content.startswith(f"{PREFIXO}pivoz "):
        pergunta = message.content[len(f"{PREFIXO}pivoz "):]
        vc = message.guild.voice_client
        if not vc:
            await message.channel.send("Me chama pra call primeiro com `!entrar`!")
            return
        try:
            texto = await perguntar_groq(user_id, pergunta)
            await message.channel.send(f"🎙️ {texto}")
            tts = gTTS(text=texto, lang="pt")
            tts.save("resposta.mp3")
            if not vc.is_playing():
                vc.play(discord.FFmpegPCMAudio("resposta.mp3"))
        except Exception as e:
            await message.channel.send(f"Erro: {e}")

client.run(DISCORD_TOKEN)
