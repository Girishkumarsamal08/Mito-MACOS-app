import pygame
import random
import asyncio
 
import os
from dotenv import dotenv_values



env_vars = dotenv_values(".env")
Assistantvoice = env_vars.get("AssistantVoice") or "en-US-AriaNeural"

async def TextToAudioFile(text) -> None:
    try:
        from gtts import gTTS

        file_path = "Data/speech.mp3"

        if os.path.exists(file_path):
            os.remove(file_path)

        tts = gTTS(text=text, lang="en")
        tts.save(file_path)

    except Exception as e:
        print(f"[MITO TTS] Audio generation failed: {e}")
        raise


def TTS(Text, func=lambda r=None: True):
    try:
        asyncio.run(TextToAudioFile(Text))
        file_path = "Data/speech.mp3"
        
        # Try macOS native afplay first for fast, reliable audio output
        if os.path.exists(file_path):
            import subprocess
            res = subprocess.run(["afplay", file_path])
            if res.returncode == 0:
                return True

        # Fallback to pygame.mixer
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            try:
                if callable(func):
                    if func() == False:
                        break
            except Exception as callback_error:
                print(f"[MITO TTS callback error] {callback_error}")
                break

            pygame.time.Clock().tick(10)

        return True
    except Exception as e:
        print(f"error in tts : {e}")
        return False
    finally:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass

def TextToSpeech(Text,func=lambda r=None: True):
    Data = str(Text).split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:1])+". "+random.choice(responses),func)
    else:
        TTS(Text,func) 

if __name__=="__main__":
   while True:
       TextToSpeech(input("Enter the text: "))