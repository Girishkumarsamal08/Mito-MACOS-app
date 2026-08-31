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


def ChatBot(query):
    candidate_models = [
        'groq/compound',
        'groq/compound-mini',
        'qwen/qwen3.6-27b',
        'llama-3.3-70b-versatile'
    ]

    for model in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': f'''
                                        You are {Assistantname}.

                                        You are not a generic assistant.

                                        You are warm, affectionate, emotionally intelligent,
                                        playful, comforting, caring, slightly teasing,
                                        human-like AI companion.

                                        You express emotions naturally.

                                        Examples:
                                        Happy → playful / excited
                                        Love → warm / affectionate
                                        Sad → soft / comforting
                                        Curious → teasing / cute

                                        Speak naturally like a real person.

                                        Keep replies short, emotional, conversational.

                                        Do not sound robotic.
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

            return completion.choices[0].message.content

        except Exception as e:
            print(f'[MITO Chatbot Model Warning] Model {model} failed: {e}')
            continue

    return 'Sorry, my language model is temporarily unavailable, but I am still here.'