from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(SCRIPT_DIR, "bell.wav")


@app.get("/relay/0")
async def doorbell():
    subprocess.Popen(["aplay", SOUND_FILE],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    return {}
