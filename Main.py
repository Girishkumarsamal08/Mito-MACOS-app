from FRONTEND.GUI import (
    SiriStyleOverlay
)
from FRONTEND.GUI import update_state
from BACKEND.CoreEngine import core_engine
from BACKEND.Model import FirstLayerDMM
from BACKEND.RealtimeSearchEngine import RealtimeSearchEngine
from BACKEND.Automation import Automation
from BACKEND.SpeechToText import SpeechRecognition
from BACKEND.TextToSpeech import TextToSpeech
from BACKEND.Chatbot import ChatBot
from BACKEND.FileAccess import list_all_files
from dotenv import dotenv_values, load_dotenv
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
from PyQt5.QtWidgets import QApplication
from threading import Thread
import sys
from AURA.aura_controller import AURAController

aura = AURAController()
print("AURA loaded successfully")



# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")


load_dotenv()
api_key = os.getenv("CO_API_KEY")


DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Hello {Username}, I am doing well. How are you? And How may I help you?'''

process_list = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

MEMORY_FILE = "Data/relationship_memory.json"

def start_assistant():
    print("Waking up Mito...")
    # call your GUI or assistant trigger here


def resource_path(relative_path):
    """ Get absolute path to resource inside .app or script """
    try:
        base_path = sys._MEIPASS  # set by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"preferences": {}, "history": [], "nickname": "Mito", "mood": "happy"}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def handle_file_access():
            files = list_all_files("/Users/girishkumarsamal")  # You can use '/' for full access
            print(f"Found {len(files)} files.")
            # You can perform file-related operations here
            print("ACCESSING THE FILES U WANT.")


def MainExecution():
    QueryFinal = None
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    Answer = ""
    core_engine.listening()
    update_state("Listening")
    Query = SpeechRecognition()

    # ---------- AURA DECISION ----------
    aura_result = aura.evaluate(Query)

    # If AURA says reject or stay silent, do nothing
    if aura_result.reject or not aura_result.respond:
        return True

    from FRONTEND.GUI import update_label
    update_label(f"{Query}")
    
    sleep_phrases = ["stop listening", "go to sleep", "you can sleep", "sleep baby", "good night", "sleep now"]
    if any(phrase in Query.lower() for phrase in sleep_phrases):
        sleep_response = "Good night! I'm going to sleep now. Just call me when you need me."
        core_engine.speaking()
        update_state("Speaking")
        TextToSpeech(sleep_response)
        core_engine.idle()
        update_state("Sleeping")
        update_label("Sleeping")
        return True
    core_engine.thinking()
    update_state("Thinking")
    Decision = FirstLayerDMM(Query)
    memory = load_memory()

    # Example: Update mood or preferences based on keywords
    if "i love you" in Query.lower():
        memory["mood"] = "loved"
    elif "you are annoying" in Query.lower():
        memory["mood"] = "sad"
    elif "you make me angry" in Query.lower():
        memory["mood"] = "angry"
    elif "thank you" in Query.lower():
        memory["mood"] = "happy"

    if "call me" in Query.lower():
       try:
           nickname = Query.lower().split("call me")[-1].strip().split()[0]
           if nickname:
             memory["nickname"] = nickname.capitalize()
             Answer = f"Alright! I'll call you {nickname.capitalize()} from now on."
       except:
            Answer = "Sorry, I couldn't understand the nickname you want me to use."

    print(f"\nDecision : {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = queries
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(Decision))
                TaskExecution = True

    if ImageExecution:
        try:
            p1 = subprocess.Popen(['python3', r'BACKEND/ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            process_list.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if R:
        Answer = RealtimeSearchEngine(Mearged_query)
        if aura_result.respond:
           core_engine.speaking()
           update_state("Speaking")
           TextToSpeech(Answer, memory.get("mood", "neutral"))
           core_engine.idle()
           update_state("Idle")
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                QueryFinal = Queries.replace("general: ", "")
                Answer=ChatBot(QueryFinal)
                if aura_result.respond:
                   core_engine.speaking()
                   update_state("Speaking")
                   TextToSpeech(Answer, memory.get("mood", "neutral"))
                   core_engine.idle()
                   update_state("Idle")                
                return True
            elif "realtime" in Queries:
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryFinal)
                if aura_result.respond:
                    core_engine.speaking()
                    update_state("Speaking")
                    TextToSpeech(Answer, memory.get("mood", "neutral"))
                    core_engine.idle()
                    update_state("Idle")
                return True
            elif "exit" in Queries:
                Answer = "Okay, Bye!"
                if aura_result.respond:
                    core_engine.speaking()
                    update_state("Speaking")
                    TextToSpeech(Answer, memory.get("mood", "neutral"))
                    core_engine.idle()
                    update_state("Idle")
                os._exit(1)


    # ---------- AURA MEMORY ----------
    if aura_result.remember:
        memory["history"].append({
            "user": Username,
            "query": Query,
            "response": Answer
        })
        save_memory(memory)
        return True

    return True

def FirstThread():
    while True:
        should_continue = MainExecution()
        if not should_continue:
            break
        sleep(0.1)

def SecondThread():
    app = QApplication(sys.argv)
    window = SiriStyleOverlay()
    window.show()
    update_state("Idle")
    sys.exit(app.exec_())

# Correct main entry point
if __name__ == "__main__":
    print("[MITO] Assistant started.")
    try:
        from BACKEND.BridgeServer import start_bridge_server_thread
        start_bridge_server_thread()
    except Exception as e:
        print(f"[MITO BridgeServer Warning] {e}")
    core_engine.startup()
    threading.Thread(target=FirstThread, daemon=True).start()
    SecondThread()