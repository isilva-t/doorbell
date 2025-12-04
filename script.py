from fastapi import FastAPI
import subprocess
import os
from datetime import datetime

app = FastAPI()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(SCRIPT_DIR, "bell.wav")


@app.get("/relay/0")
async def doorbell():
    result = subprocess.Popen(["aplay", "-D", "plughw:0,0", SOUND_FILE],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    return {
        "status": "triggered",
        "timestamp": datetime.now().isoformat(),
        "sound_file": SOUND_FILE,
        "pid": result.pid
    }
