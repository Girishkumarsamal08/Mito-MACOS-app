import os
import subprocess
import base64
from groq import Groq
from dotenv import dotenv_values

env_vars = dotenv_values('.env')
GroqAPIKey = env_vars.get('GroqAPIKey')
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

def get_active_window_info():
    cmd = '''
    tell application "System Events"
        set activeApp to name of first application process whose frontmost is true
        set windowName to ""
        try
            tell process activeApp
                set windowName to name of front window
            end tell
        end try
        return activeApp & " - " & windowName
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def capture_screen(output_path="/tmp/mito_screen.png"):
    # Method 1: screencapture -x
    try:
        res = subprocess.run(["screencapture", "-x", output_path], capture_output=True)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
    except Exception:
        pass

    # Method 2: screencapture standard
    try:
        res = subprocess.run(["screencapture", output_path], capture_output=True)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
    except Exception:
        pass

    # Method 3: PIL ImageGrab
    try:
        from PIL import ImageGrab
        im = ImageGrab.grab()
        im.save(output_path)
        return output_path
    except Exception:
        pass

    return None

def analyze_screen(prompt="What is the user doing on screen?"):
    active_win = get_active_window_info()
    image_path = capture_screen()
    
    if not image_path or not os.path.exists(image_path):
        if active_win:
            return f"Master, aap abhi {active_win} pe kaam kar rahe ho! Oh acha thik h!"
        return "Master, main aapki screen abhi dekh nahi paayi."

    if not client:
        if active_win:
            return f"Master, aap abhi {active_win} open karke baithe ho!"
        return "Groq API key missing."

    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        context_hint = f"Active window: {active_win}" if active_win else ""

        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"You are MITO, a warm, affectionate, cute AI companion. {context_hint}. "
                                "Describe what Master is doing on screen in 1-2 short, natural Hinglish/English sentences. "
                                "Address the user as Master (e.g., 'Master, aap toh... kar rahe ho! ... Oh acha thik h!'). Be cute and friendly!"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=250
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[MITO Vision Error] {e}")
        if active_win:
            return f"Master, aap abhi {active_win} pe ho! Oh acha thik h!"
        return "Master, main dekh rahi hu aap screen pe busy ho!"
