# 💀 DIGITAL PHANTOM HUNTER

> *“Hunt the threat before it hunts you.”*

**DIGITAL PHANTOM HUNTER** is a cinematic, spooky cybersecurity investigation workstation engineered to dissect suspicious SMS smishing, phishing emails, deceptive URLs, and screenshot evidence before users fall victim. Powered by **Google Gemma** neural threat intelligence with an autonomous fallback heuristics engine.

---

## ⚡ Features

| Capability | Tactical Description |
|---|---|
| 📩 **Triple Modality Scanner** | Inspect raw text (SMS/emails), deceptive URLs, and uploaded screenshot artifacts. |
| 🧠 **Google Gemma Integration** | Calls Google's Gemma models (`gemma-3-27b-it`, `gemma-3-12b-it`, `gemini-2.5-flash`) via secure backend proxy. |
| 🛡️ **Zero-Credential Demo Mode** | When no API key is supplied, automatically falls back to the deterministic Phantom Cyber-Heuristics engine with explicit UI labeling. |
| 📊 **Dynamic Tactical Threat Meter** | 0–100 threat gauge classifying payloads into **LOW 🟢 / MEDIUM 🟡 / HIGH 🔴** with live DEFCON status. |
| 🎯 **Forensic Token Highlighter** | Interactive text viewer that highlights malicious phrases (`within 24 hours`, `confirm password`) with clickable threat explanations. |
| 🛰️ **Interactive Radar HUD** | 360° phosphor radar display tracking detected Indicators of Compromise (IOCs) with interactive blips and synthesized audio cues. |
| ⚡ **Instant Demo Presets** | One-click preloads for Chase Bank Smishing, Microsoft 365 Password Phishing, Web3 Crypto Drainer, USPS Parcel Scam, and a Benign GitHub Notice. |
| 📚 **Phantom Threat Codex** | Searchable cyber-safety knowledge base with category filters, interactive scam anatomy visualizer, and "Spot the Phantom" threat quiz. |
| 🗄️ **Investigation History** | Client-side persistent archive of past scans with JSON export and instant dossier recall. |

---

## 🎨 Secret Cyber Investigation Lab Aesthetic

- **Color Palette:** Void black (`#03070a`), neon cyber-green (`#00ff66`), crimson red alert (`#ff0033`), amber warning (`#f59e0b`).
- **Visual FX:** Dynamic CRT scanline overlay, rotating radar sweep beam, alert beacon flashing, chromatic aberration glitch animations, and terminal diagnostic stream.
- **Audio Synthesizer:** Built-in Web Audio API synthesizer for tactile radar pings, scanner drones, and warning sirens (with mute/unmute toggle).

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Node.js** (v18+ or v24+ recommended)
- **npm** (v9+ or v11+)

### 1. Start the Application
From the workspace root directory:

```bash
# Start both Backend Server (port 3001) and Frontend Client (port 5173) concurrently
npm run dev
```

Alternatively, from the `phobos/` directory:
```bash
cd phobos
npm run dev
```

Open your browser at **http://localhost:5173**.

---

## 🔑 Configuring Google Gemma API (Optional)

Digital Phantom Hunter is fully functional out of the box in **Demo Heuristic Mode** with zero API keys required.

To connect live Google Gemma models:
1. Obtain a free API key at **[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)**.
2. Edit `phobos/.env`:
   ```ini
   PORT=3001
   GEMMA_PROVIDER=gemini-api
   GEMMA_API_KEY=your_google_ai_studio_api_key_here
   GEMMA_MODEL_ID=gemma-3-27b-it
   ```
3. Restart the server. The UI badge will automatically update to **⚡ LIVE GEMMA ACTIVE**.
> **Security Notice:** API keys are stored strictly server-side in `.env` and never leaked into the client bundle.

---

## 🧪 Testing & Verification

Run the automated security heuristics test suite:
```bash
cd phobos/server
npx tsx src/test-runner.ts
```

Run HTTP API verification smoke tests:
```bash
cd phobos/server
npm test
```

---

## 🔒 Privacy & Safety Notice

- **Confidentiality:** Payloads and screenshots are processed in ephemeral server memory. Personal Identifiable Information (PII) should always be redacted before scanning.
- **AI Disclaimer:** Automated threat models provide probabilistic risk evaluations and educational indicators. A **LOW** score indicates no active threat signatures were observed, but cannot guarantee 100% safety. Never share passwords, seed phrases, or MFA codes with unsolicited contacts.
