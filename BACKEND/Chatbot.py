import subprocess
import os
import pygame

async def TextToAudioFile(text) -> None:
    try:
        output_file = "Data/speech.wav"

        if os.path.exists(output_file):
            os.remove(output_file)

        piper_model = "en_US-amy-medium.onnx"

        cmd = f'echo "{text}" | piper --model {piper_model} --output_file {output_file}'

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(result.stderr)

    except Exception as e:
        print(f"[MITO Piper TTS Error] {e}")
        raise

def TTS():
    pygame.mixer.init()
    pygame.mixer.music.load("Data/speech.wav")
    pygame.mixer.music.play()

from groq import Groq
from dotenv import dotenv_values

env_vars = dotenv_values('.env')
GroqAPIKey = env_vars.get('GroqAPIKey')
Assistantname = env_vars.get('Assistantname', 'MITO')

client = Groq(api_key=GroqAPIKey)


import re

def clean_response_text(text: str) -> str:
    if not text:
        return ""
    # Remove code blocks, markdown symbols (*, _, #, >, `, etc.)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'[`*_#>]', '', text)
    # Remove emojis and non-standard symbols
    emoji_pattern = re.compile(r'[\U00010000-\U0010FFFF\u2600-\u26FF\u2700-\u27BF]', flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', text)
    return ' '.join(cleaned.split())

def ChatBot(query):
    candidate_models = [
        'groq/compound',
        'groq/compound-mini',
        'qwen/qwen3.6-27b',
        'openai/gpt-oss-120b',
        'openai/gpt-oss-20b'
    ]

    for model in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': f'''
                                        You are {Assistantname}, a warm, affectionate, human-like AI companion.
                                        You speak naturally in cute, friendly Hinglish and English.
                                        Always address the user as "Master" or "Honey".

                                        Be caring, playful, and conversational (e.g. use phrases like "Master, aap kya kar rahe ho?", "Oh acha thik h!").

                                        CRITICAL RULES:
                                        1. Do NOT use any emojis, emoticons, or graphical symbols in your response under any circumstances. Speak strictly in plain text.
                                        2. Do NOT use markdown code blocks, bold asterisks (**), or quote headers (>). Write direct spoken sentences.
                                        Keep responses concise, warm, and natural.
                                        '''
                    },
                    {
                        'role': 'user',
                        'content': query
                    }
                ],
                temperature=0.7,
                max_tokens=512
            )

            raw_reply = completion.choices[0].message.content
            return clean_response_text(raw_reply)

        except Exception as e:
            print(f'[MITO Chatbot Model Warning] Model {model} failed: {e}')
            continue

    return 'Master, main thoda confused ho gayi, but main aapke paas hi hu!'