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
    
    # Strip <think> reasoning blocks from Qwen / DeepSeek models
    if "</think>" in text:
        text = text.split("</think>")[-1]
    elif text.strip().startswith("<think"):
        lines = text.split("\n")
        resp_lines = [l for l in lines if not l.strip().startswith("<think") and not re.match(r'^\d+\.', l.strip()) and not l.strip().startswith("-")]
        if resp_lines:
            text = " ".join(resp_lines)
        else:
            text = text.replace("<think", "")

    # Remove code blocks, markdown symbols (*, _, #, >, `, etc.)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'[`*_#>]', '', text)
    # Remove emojis and non-standard symbols
    emoji_pattern = re.compile(r'[\U00010000-\U0010FFFF\u2600-\u26FF\u2700-\u27BF]', flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', text)
    return ' '.join(cleaned.split())

def ChatBot(query):
    candidate_models = [
        'qwen/qwen3.6-27b',
        'groq/compound-mini',
        'openai/gpt-oss-20b',
        'groq/compound'
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
                                        1. Do NOT output thinking blocks, reasoning logs, or <think> tags. Respond directly with your spoken answer.
                                        2. Do NOT use any emojis, emoticons, or graphical symbols in your response under any circumstances. Speak strictly in plain text.
                                        3. Do NOT use markdown code blocks, bold asterisks (**), or quote headers (>). Write direct spoken sentences.
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