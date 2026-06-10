# L U N A  v2.0

A Siri-like personal AI assistant with full device control, personal intelligence, and advanced capabilities.

## Features

- **Natural conversation** — context-aware, remembers topics, learns your habits
- **Phone control** — SMS, calls, contacts, apps, WiFi, Bluetooth, brightness
- **System control** — CPU, RAM, battery, network, storage
- **Camera vision** — identify objects, plants, text, scenes (via llava)
- **Screen understanding** — sees and analyzes your screen
- **Smart home** — control WLED, Tasmota, MQTT, and HTTP IoT devices
- **Internet agent** — search, research, weather, news, package tracking
- **Automation** — multi-step workflows, morning/evening routines
- **Finance** — expense tracking, budgets, bills, insights
- **Health coach** — activity, meals, sleep, water, goals
- **Creative** — code generation, design ideas, story writing
- **Personal intelligence** — learns name, preferences, predicts needs
- **Siri-like voice** — varied responses, natural cadence, warm tone

## Build APK

### Option 1: GitHub Actions (easiest)

1. Push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Luna v2.0"
   # Create repo on GitHub.com, then:
   git remote add origin https://github.com/YOU/luna.git
   git push -u origin main
   ```
2. Go to **Actions** → **Build Luna APK** → **Run workflow**
3. Download APK from **Artifacts** (~25 min)

### Option 2: Google Colab

Upload `https://colab.research.google.com` and run.

### Option 3: Local WSL/Linux

```bash
buildozer android debug
```

## Connect to Ollama

```bash
ollama pull mistral
ollama serve
```
Set `ollama_host` in `config.json` to your PC's IP for Android use.

## License

MIT
