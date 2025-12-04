# Doorbell HTTP to Audio System

Simple FastAPI server that plays audio when receiving HTTP requests.
Designed to serve as spare solution, to quick replace a dead slave Shelly relay in a doorbell system.

## Overview

When a Shelly button is pressed, it sends an HTTP request to this server, which plays an audio file through the system speakers. 
The service runs at boot, play the bell sound, without requiring user login.

## Architecture
```
Physical Setup:

┌──────────────┐
│ Doorbell     │
│ Button       │ (Physical press)
└──────┬───────┘
       │
       │ (Wired)
       ▼
┌──────────────┐
│ Master       │
│ Shelly       │◄────┐
│ (WiFi)       │     │
└──────────────┘     │
       │             │
       │ HTTP GET    │  WiFi Network
       │             │
       ▼             │
┌──────────────┐     │
│   Router     │◄────┤
│   (WiFi)     │     │
└──────────────┘     │
       │             │
       │             │
       ▼             │
┌──────────────┐     │
│ Ubuntu PC    │◄────┘
│ (WiFi)       │
│ Port 8000    │
│ + Speakers   │
└──────────────┘

Previously (when slave Shelly working):
Button → Master Shelly → Router → Shelly (slave) → Buzzer

Current solution:
Button → Master Shelly → Router → Ubuntu PC → Audio playback

When I got slave Shelly replaced, it will have redundant bell system.
Button → Master Shelly → Router → Ubuntu PC → Audio playback
                                → Shelly (slave) → Buzzer

```
## Components

- **script.py** - FastAPI server with `/relay/0` endpoint
- **bell.wav** - Audio file to play (replace with your own)
- **doorbell.service.example** - Systemd service template

## Requirements for simple setup

- Ubuntu Desktop (tested on 22.04 LTS)
- Python 3 with pip
- Audio output (speakers/headphones)
- Need fixed IP address on LAN for your PC (could set on router DHCP)
- sudo privileges for install

## Installation

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip
pip3 install fastapi uvicorn
```

### 2. Clone and Setup
```bash
git clone git@github.com:isilva-t/doorbell.git
cd doorbell
```

Place your audio file as `bell.wav` or update the `SOUND_FILE` path in `script.py`.

### 3. Verify Audio Device
```bash
aplay -l
```

Note your card and device (e.g., card 0, device 0 = `plughw:0,0`). Update the `-D` parameter in `script.py` if different:
```python
subprocess.Popen(["aplay", "-D", "plughw:0,0", SOUND_FILE], ...)
```

### 4. Add User to Audio Group
```bash
sudo usermod -a -G audio $USER
```

Logout/login or reboot for changes to take effect.

### 5. Test Manually
```bash
python3 -m uvicorn script:app --host 0.0.0.0 --port 8000
```

From another terminal in same computer:
```bash
curl http://localhost:8000/relay/0?turn=on
```
Or from a browser in other device simple open
```
http://<YOUR_PC_IP>:8000/relay/0?turn=on
```

Should play audio and return JSON response with timestamp and process info.

### 6. Install as Systemd Service

Copy and edit the service file:
```bash
sudo cp doorbell.service.example /etc/systemd/system/doorbell.service
sudo nano /etc/systemd/system/doorbell.service
```

Update these fields:
- `User=` - your username
- `WorkingDirectory=` - full path to doorbell directory

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable doorbell
sudo systemctl start doorbell
sudo systemctl status doorbell
```

### 7. Configure Shelly Button

In your Shelly master device web interface, configure the button action URL:
```
http://[YOUR_PC_IP]:8000/relay/0?turn=on
```

## API Endpoint

**GET** `/relay/0?turn=on`

**Note:** The Shelly device doesn't care about the response - it just fires the request and continues.
The JSON response was added purely for testing/debugging purposes.


Response:
```json
{
  "status": "triggered",
  "timestamp": "2025-12-04T12:30:45.123456",
  "sound_file": "/path/to/bell.wav",
  "pid": 12345
}
```

## Troubleshooting

### Check service status
```bash
sudo systemctl status doorbell
journalctl -u doorbell -n 50
```

### Service not playing audio when locked/logged out
Ensure:
- User is in `audio` group: `groups $USER`
- ALSA device is correct: test with `aplay -D plughw:0,0 bell.wav`
- Service uses correct device in script

### Check if port is listening
```bash
sudo netstat -tlnp | grep 8000
```

### Restart service after changes
```bash
sudo systemctl restart doorbell
```

## How It Works

1. Shelly button pressed → HTTP GET to YOUR_PC_IP `/relay/0?turn=on`
2. FastAPI receives request
3. Spawns `aplay` subprocess in background
4. Audio plays through ALSA device
5. Returns JSON response immediately
6. Ready for next request

The service uses ALSA directly (`plughw:0,0`) instead of PulseAudio to work without user session, 
allowing it to function at boot, when locked, or when no user is logged in.

## License
MIT
