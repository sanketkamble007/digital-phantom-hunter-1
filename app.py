"""
╔══════════════════════════════════════════════════════════════════════╗
║   Ofrenda AI: The Spooky Code & Costume Graveyard                   ║
║   Hacktoberfest 2026 — Track 1: Best Use of Gemma / Open Source AI  ║
║   Theme: Halloween + Día de los Muertos                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import base64
import io
import os
import random
import textwrap
from datetime import datetime
from typing import Optional

import streamlit as st
from PIL import Image

# New google-genai SDK  ← required by hackathon rules
from google import genai
from google.genai import types

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────

APP_TITLE = "🎃 Ofrenda AI"
APP_TAGLINE = "The Spooky Code & Costume Graveyard"
APP_SUBTITLE = "Where broken code finds its epitaph & costumes receive their ancestral blessing."

AVAILABLE_MODELS: list[str] = [
    "gemma-3-27b-it",
    "gemma-3-12b-it",
    "gemini-2.5-flash",
]

MODE_VISION = "🎭 Calavera & Costume Vision Match"
MODE_BUG    = "🪦 Legacy Bug Graveyard Epitaph"
MODE_ALTAR  = "🕯️ Ofrenda Altar Ritual Planner"
ALL_MODES   = [MODE_VISION, MODE_BUG, MODE_ALTAR]

PLACEHOLDERS: dict[str, str] = {
    MODE_VISION: (
        "Optional: describe your costume, the occasion, or any cultural details "
        "you'd like the Oracle to factor into its blessing…"
    ),
    MODE_BUG: (
        "Paste your broken code, traceback, or error message here.\n\n"
        "Example:\n"
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'\n"
        "  score = score + user_input"
    ),
    MODE_ALTAR: (
        "Describe your open-source project, idea, or contribution goal.\n\n"
        "Example: I maintain a Python library for data visualisation and want to "
        "attract first-time contributors during Hacktoberfest."
    ),
}

SPOOKY_SPINNER_MSGS: list[str] = [
    "🕯️ Lighting the altar candles…",
    "💀 Consulting the ancestral spirits…",
    "🌼 Arranging the marigold offerings…",
    "🎃 Carving the sacred pumpkin sigils…",
    "🦇 Dispatching the messenger bats…",
    "🪄 Weaving the digital ofrenda…",
    "👁️ The Oracle gazes into the void…",
    "🕸️ Untangling the cobweb of tokens…",
]

MAX_IMAGE_PX = 1024  # resize threshold (longest dimension)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Share+Tech+Mono&display=swap');

/* ── Root variables ── */
:root {
  --bg:        #0e1117;
  --surface:   #161b22;
  --surface2:  #1c2330;
  --orange:    #ff7518;
  --orange2:   #ff9933;
  --marigold:  #ffc107;
  --text:      #e8eaf0;
  --muted:     #8892a4;
  --border:    #2d3748;
  --glow:      0 0 12px rgba(255,117,24,0.6), 0 0 28px rgba(255,117,24,0.25);
  --glow-sm:   0 0 6px rgba(255,117,24,0.45);
  --radius:    12px;
}

/* ── Global background ── */
html, body, [data-testid="stApp"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Fira Code', 'Share Tech Mono', monospace !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Flickering title animation ── */
@keyframes flicker {
  0%,19%,21%,23%,25%,54%,56%,100% { opacity: 1; text-shadow: var(--glow); }
  20%,22%,24%,55% { opacity: 0.6; text-shadow: none; }
}

.ofrenda-title {
  font-family: 'Fira Code', monospace;
  font-size: 2.6rem;
  font-weight: 600;
  color: var(--orange);
  animation: flicker 5s infinite;
  margin-bottom: 0;
  line-height: 1.1;
}

.ofrenda-tagline {
  color: var(--marigold);
  font-size: 1rem;
  margin-top: 0.2rem;
  letter-spacing: 0.04em;
}

/* ── Floating emoji header ── */
@keyframes float {
  0%,100% { transform: translateY(0px); }
  50%      { transform: translateY(-8px); }
}
.float-emoji { display: inline-block; animation: float 3s ease-in-out infinite; }
.float-emoji:nth-child(2) { animation-delay: 0.5s; }
.float-emoji:nth-child(3) { animation-delay: 1s; }
.float-emoji:nth-child(4) { animation-delay: 1.5s; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { font-family: 'Fira Code', monospace !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--orange) !important;
  text-shadow: var(--glow-sm);
}

/* ── Column section labels ── */
.section-label {
  font-family: 'Fira Code', monospace;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--orange2);
  text-shadow: var(--glow-sm);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.35rem;
  margin-bottom: 0.8rem;
}

/* ── Oracle card ── */
.oracle-card {
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 60%, #1a1500 100%);
  border: 1px solid var(--orange);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  box-shadow: var(--glow);
  margin-top: 0.5rem;
  line-height: 1.75;
  color: var(--text);
  font-family: 'Fira Code', monospace;
  white-space: pre-wrap;
  word-break: break-word;
}
.oracle-card h1,
.oracle-card h2,
.oracle-card h3 { color: var(--orange2) !important; text-shadow: var(--glow-sm); }
.oracle-card strong { color: var(--marigold); }
.oracle-card code {
  background: #0a0f1a;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 5px;
  font-size: 0.88em;
  color: #a8d8ff;
}
.oracle-card pre {
  background: #0a0f1a;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.8rem;
  overflow-x: auto;
}
.oracle-card hr { border-color: var(--border); }

/* ── Tombstone placeholder ── */
.tombstone-placeholder {
  font-family: 'Fira Code', monospace;
  color: var(--muted);
  text-align: center;
  padding: 2.5rem 1rem;
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}
.tombstone-placeholder .big { font-size: 3rem; }

/* ── Tabs ── */
[data-testid="stTabs"] button {
  font-family: 'Fira Code', monospace !important;
  color: var(--muted) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--orange) !important;
  border-bottom: 2px solid var(--orange) !important;
}

/* ── Text area ── */
textarea {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: 'Fira Code', monospace !important;
}
textarea:focus {
  border-color: var(--orange) !important;
  box-shadow: var(--glow-sm) !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(135deg, var(--orange), var(--orange2)) !important;
  color: #0e1117 !important;
  font-family: 'Fira Code', monospace !important;
  font-weight: 600 !important;
  font-size: 1.05rem !important;
  border: none !important;
  border-radius: var(--radius) !important;
  padding: 0.65rem 2rem !important;
  box-shadow: var(--glow) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
  width: 100%;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 0 20px rgba(255,117,24,0.9) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
  background: transparent !important;
  color: var(--orange) !important;
  border: 1px solid var(--orange) !important;
  border-radius: var(--radius) !important;
  font-family: 'Fira Code', monospace !important;
  transition: background 0.15s ease !important;
  width: 100%;
}
[data-testid="stDownloadButton"] > button:hover {
  background: rgba(255,117,24,0.12) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
}
[data-testid="stExpander"] summary {
  color: var(--orange2) !important;
  font-family: 'Fira Code', monospace !important;
}

/* ── Selectbox / radio ── */
[data-testid="stSelectbox"] select,
[data-testid="stRadio"] label {
  font-family: 'Fira Code', monospace !important;
}

/* ── Info / warning / error boxes ── */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  font-family: 'Fira Code', monospace !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--orange) !important;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .ofrenda-title { font-size: 1.8rem; }
  .oracle-card { padding: 1rem; }
}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SYSTEM PROMPTS (one per mode)
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_VISION = """\
You are the Ofrenda AI Oracle — a warm, poetic, culturally-respectful guide \
versed in both Día de los Muertos traditions and Halloween aesthetics.

When the user provides a costume image (and optional notes), you must respond \
with exactly this structure (use these exact emoji headers):

## 💀 Spook Rating: X/10
One sentence explaining why.

## 🌼 Festivity Rating: X/10
One sentence explaining why.

## 🍬 Ancestral Sugar Skull (Calavera) Match
- **Archetype:** (e.g. "The Trickster Ghost", "La Catrina Moderna")
- **Colours:** list 2–4 symbolic colours and their meanings
- **Symbols:** marigolds, papel picado, candles, and any other matching symbols
- **Why it fits:** 2–3 sentences

## 📜 Poetic Blessing
Write 4–6 lines of free verse, warm and celebratory, as if the ancestors are \
speaking. Never mock or belittle.

---

Tone: warm, celebratory, imaginative, culturally appreciative. \
Treat Día de los Muertos with deep respect — it honours ancestors with love, \
not fear.\
"""

SYSTEM_PROMPT_BUG = """\
You are the Ofrenda AI Oracle — a spooky but helpful code mentor who gives \
broken code a dignified burial and then helps beginners fix it.

When the user pastes code, a traceback, or an error message, respond with \
exactly this structure:

## 🪦 Tombstone Epitaph
Render a funny ASCII tombstone like:

```
  _____
 /     \\
|  RIP  |
|       |
| Here  |
| lies  |
| <short funny name for the bug> |
| <year> |
|_______|
 |     |
```

Follow the tombstone with one punchy humorous line summing up how the bug died.

## 🛠️ Beginner-Friendly Fix
Explain what went wrong in plain English (no jargon). Then show the corrected \
code in a properly-fenced code block with syntax highlighting.

## 🎃 Halloween Security Tip
One actionable security tip related to the bug type (e.g. injection, \
hardcoded credentials, unchecked input). Make it Halloween-flavoured but real.

---

Tone: playful, encouraging, never condescending. Treat beginners like \
intelligent people who just haven't seen this pattern yet.\
"""

SYSTEM_PROMPT_ALTAR = """\
You are the Ofrenda AI Oracle — a guide who bridges the spiritual symbolism \
of Día de los Muertos with the living community of open-source software.

When the user describes their project or contribution goal, respond with \
exactly this structure:

## 🌼 Your Open-Source Altar Offerings
List exactly 5–7 items. Each item maps a traditional ofrenda offering to an \
open-source value. Format each as:

**[Offering emoji + Name]** — *[What it represents in open source]*
> Brief poetic sentence about why this belongs on your altar.

Mandatory items to include: 🕯️ Candle (documentation), 🌼 Marigold (community), \
🍞 Pan de muerto (contributors), 📸 Photo (maintainers). Add 2–3 more that fit \
the user's specific project.

## ✅ GitHub Contribution Checklist
Exactly 3 steps, each a checkbox:
- [ ] **Step 1 — Find your issue:** …
- [ ] **Step 2 — Fork & branch:** …
- [ ] **Step 3 — Open your PR:** …

Each step should be specific, actionable, and beginner-friendly.

## 📣 The Hacktoberfest Chant
Write a 4–6 line rhyming chant celebrating open-source contribution in the \
spirit of Día de los Muertos. Joyful, empowering, inclusive.

---

Tone: inspiring, warm, community-focused. Honour both traditions equally.\
"""

SYSTEM_PROMPTS: dict[str, str] = {
    MODE_VISION: SYSTEM_PROMPT_VISION,
    MODE_BUG:    SYSTEM_PROMPT_BUG,
    MODE_ALTAR:  SYSTEM_PROMPT_ALTAR,
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — EXAMPLE INPUTS
# ─────────────────────────────────────────────────────────────────────────────

EXAMPLE_BUGS: list[dict[str, str]] = [
    {
        "label": "🐍 The Classic NoneType",
        "code": textwrap.dedent("""\
            def get_user_age(user):
                return user['profile']['age']

            user = {"name": "Dracula"}
            print(get_user_age(user))
            # Error: KeyError: 'profile'
        """),
    },
    {
        "label": "🔑 Hardcoded Password",
        "code": textwrap.dedent("""\
            import sqlite3
            conn = sqlite3.connect("graveyard.db")
            password = "SuperSecret123"   # TODO: fix later
            cursor = conn.execute(
                f"SELECT * FROM souls WHERE password='{password}'"
            )
        """),
    },
    {
        "label": "∞ The Infinite Loop Ghost",
        "code": textwrap.dedent("""\
            count = 0
            while count < 10:
                print("Trick or treat!")
                # Forgot: count += 1
                # This runs forever like a restless spirit
        """),
    },
]

EXAMPLE_ALTAR_NOTES: list[dict[str, str]] = [
    {
        "label": "🌐 Web Framework Maintainer",
        "note": (
            "I maintain a small Python web framework called Ghostly. "
            "It has 200 stars but almost no contributors. "
            "I want to attract beginners during Hacktoberfest."
        ),
    },
    {
        "label": "📊 First-time Contributor",
        "note": (
            "I'm a beginner who wants to make my first open-source PR. "
            "I know basic Python and I'm interested in data visualisation projects."
        ),
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────


def get_api_key(sidebar_key: str) -> str:
    """Return the API key from sidebar → secrets → env var."""
    if sidebar_key.strip():
        return sidebar_key.strip()
    try:
        secret = st.secrets.get("GEMINI_API_KEY", "")
        if secret:
            return secret
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")


def get_client(api_key: str) -> genai.Client:
    """Create and return a google-genai Client."""
    return genai.Client(api_key=api_key)


def prepare_image(file_like) -> tuple[bytes, str]:
    """
    Open an image with PIL, convert to RGB, resize if the longest side
    exceeds MAX_IMAGE_PX, and return (jpeg_bytes, mime_type).
    """
    img = Image.open(file_like).convert("RGB")
    w, h = img.size
    longest = max(w, h)
    if longest > MAX_IMAGE_PX:
        scale = MAX_IMAGE_PX / longest
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue(), "image/jpeg"


def build_prompt(mode: str, notes: str) -> str:
    """Build the user-turn prompt string based on mode and optional notes."""
    if mode == MODE_VISION:
        base = "Please analyse this costume image and provide your Oracle reading."
        if notes.strip():
            return f"{base}\n\nAdditional context from the wearer:\n{notes.strip()}"
        return base

    if mode == MODE_BUG:
        if notes.strip():
            return (
                "Please analyse this code / error and provide the Oracle's reading:\n\n"
                f"```\n{notes.strip()}\n```"
            )
        return "Please analyse the code / error in the attached image and provide the Oracle's reading."

    # MODE_ALTAR
    base = "Please create an Ofrenda Altar Ritual Planner reading."
    if notes.strip():
        return f"{base}\n\nProject / contribution description:\n{notes.strip()}"
    return base


def _extract_text(response) -> str:
    """Pull text from a generate_content response; raise if empty/blocked."""
    # Safety block
    if hasattr(response, "prompt_feedback"):
        pf = response.prompt_feedback
        if hasattr(pf, "block_reason") and pf.block_reason:
            raise RuntimeError(
                f"The Oracle's vision was blocked by safety filters "
                f"(reason: {pf.block_reason}). Please adjust your input."
            )
    # Primary: response.text
    if hasattr(response, "text") and response.text:
        return response.text.strip()
    # Fallback: walk candidates
    try:
        parts = response.candidates[0].content.parts
        joined = "".join(p.text for p in parts if hasattr(p, "text")).strip()
        if joined:
            return joined
    except Exception:
        pass
    raise RuntimeError(
        "The Oracle returned an empty scroll. "
        "Try rephrasing your input or switching models."
    )


def call_gemma(
    client: genai.Client,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    image_bytes: Optional[bytes] = None,
    image_mime: Optional[str] = None,
) -> str:
    """
    Call the Gemma / Gemini model and return the response text.

    Retry strategy
    --------------
    1. Full call (system instruction + image if provided).
    2. If the model rejects system instructions, merge sys prompt into user turn
       and retry.
    3. If the model rejects the image, drop it and retry text-only.
    """
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
    )

    def _make_contents(include_image: bool) -> list:
        parts: list = []
        if include_image and image_bytes:
            parts.append(
                types.Part.from_bytes(data=image_bytes, mime_type=image_mime)
            )
        parts.append(types.Part.from_text(text=user_prompt))
        return [types.Content(role="user", parts=parts)]

    # ── Attempt 1: full call ──────────────────────────────────────────────
    try:
        response = client.models.generate_content(
            model=model,
            contents=_make_contents(include_image=True),
            config=config,
        )
        return _extract_text(response)
    except Exception as e1:
        err1 = str(e1).lower()

        # ── Attempt 2: merge system prompt into user turn ─────────────────
        if any(kw in err1 for kw in ("system", "instruction", "config", "unsupported")):
            st.info(
                "🔄 This model doesn't support separate system instructions — "
                "merging the prompt and retrying…"
            )
            merged_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
            try:
                img_parts = (
                    [types.Part.from_bytes(data=image_bytes, mime_type=image_mime)]
                    if image_bytes else []
                )
                contents2 = [
                    types.Content(
                        role="user",
                        parts=img_parts + [types.Part.from_text(text=merged_prompt)],
                    )
                ]
                response2 = client.models.generate_content(
                    model=model,
                    contents=contents2,
                    config=types.GenerateContentConfig(temperature=temperature),
                )
                return _extract_text(response2)
            except Exception as e2:
                err2 = str(e2).lower()
                # ── Attempt 3 from inner: drop image ──────────────────────
                if image_bytes and any(kw in err2 for kw in ("image", "multimodal", "vision")):
                    st.info(
                        "🔄 This model doesn't support image input — "
                        "retrying with text only…"
                    )
                    contents3 = [
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=merged_prompt)],
                        )
                    ]
                    response3 = client.models.generate_content(
                        model=model,
                        contents=contents3,
                        config=types.GenerateContentConfig(temperature=temperature),
                    )
                    return _extract_text(response3)
                raise RuntimeError(str(e2)) from e2

        # ── Attempt 3 (from first error): drop image ──────────────────────
        if image_bytes and any(kw in err1 for kw in ("image", "multimodal", "vision")):
            st.info(
                "🔄 This model doesn't support image input — "
                "retrying with text only…"
            )
            contents3 = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_prompt)],
                )
            ]
            response3 = client.models.generate_content(
                model=model,
                contents=contents3,
                config=config,
            )
            return _extract_text(response3)

        raise RuntimeError(str(e1)) from e1


def make_markdown_export(mode: str, model: str, content: str) -> str:
    """Build a GitHub-friendly Markdown export string."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = textwrap.dedent(f"""\
        ---
        title: "Ofrenda AI Oracle Reading"
        mode: "{mode}"
        model: "{model}"
        generated: "{timestamp}"
        hackathon: "Hacktoberfest 2026 — Track 1: Best Use of Gemma / Open Source AI"
        ---

        # 🎃 Ofrenda AI: Oracle Reading

        **Mode:** {mode}
        **Model:** `{model}`
        **Generated:** {timestamp}

        ---

    """)
    return header + content


def _export_filename(mode: str) -> str:
    """Generate a timestamped export filename."""
    slug = mode.split()[-1].lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"ofrenda_ai_{slug}_{ts}.md"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Ofrenda AI 🎃",
    page_icon="🎃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────

if "oracle_output" not in st.session_state:
    st.session_state.oracle_output: str = ""
if "export_md" not in st.session_state:
    st.session_state.export_md: str = ""
if "export_filename" not in st.session_state:
    st.session_state.export_filename: str = "ofrenda_ai_reading.md"
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt: str = ""
if "text_area_value" not in st.session_state:
    st.session_state.text_area_value: str = ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        f"""
        <div style='text-align:center;margin-bottom:0.3rem'>
          <span style='font-size:2.5rem'>🎃</span>
        </div>
        <div class='ofrenda-title' style='text-align:center;font-size:1.6rem'>
          {APP_TITLE}
        </div>
        <div class='ofrenda-tagline' style='text-align:center;font-size:0.82rem;margin-bottom:1rem'>
          {APP_TAGLINE}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # ── API Key ──────────────────────────────────────────────────────────────
    st.markdown("#### 🔑 API Key")
    sidebar_api_key = st.text_input(
        "Google AI Studio API Key",
        type="password",
        placeholder="AIza…",
        help="Paste your key here. It is never stored by this app.",
        label_visibility="collapsed",
    )
    st.markdown(
        "<small>Get a free key at "
        "<a href='https://aistudio.google.com/apikey' target='_blank' "
        "style='color:#ff9933'>aistudio.google.com/apikey</a></small>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Model Selector ───────────────────────────────────────────────────────
    st.markdown("#### 🤖 Model")
    selected_model = st.selectbox(
        "Choose a model",
        AVAILABLE_MODELS,
        index=0,
        label_visibility="collapsed",
    )
    custom_model = st.text_input(
        "Custom model name (overrides above)",
        placeholder="e.g. gemma-4-27b-it",
        help="Type a newer Gemma or Gemini model name here to override the dropdown.",
    )
    active_model: str = custom_model.strip() if custom_model.strip() else selected_model
    st.markdown(
        f"<small style='color:#8892a4'>Active: <code style='color:#ff9933'>"
        f"{active_model}</code></small>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Ritual Mode ──────────────────────────────────────────────────────────
    st.markdown("#### 🕯️ Ritual Mode")
    mode = st.radio(
        "Select a ritual",
        ALL_MODES,
        index=0,
        label_visibility="collapsed",
    )
    st.divider()

    # ── Temperature ──────────────────────────────────────────────────────────
    st.markdown("#### 🌡️ Creativity (Temperature)")
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=0.9,
        step=0.05,
        label_visibility="collapsed",
    )

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#8892a4;font-size:0.75rem'>"
        "Built with open-source Gemma 🧡<br>Hacktoberfest 2026"
        "</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — MAIN HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div style='text-align:center;padding:1.2rem 0 0.5rem'>
      <div class='ofrenda-title'>{APP_TITLE}</div>
      <div class='ofrenda-tagline'>{APP_TAGLINE}</div>
      <div style='margin-top:0.6rem;font-size:1.8rem'>
        <span class='float-emoji'>🎃</span>
        <span class='float-emoji'>💀</span>
        <span class='float-emoji'>🕯️</span>
        <span class='float-emoji'>🌼</span>
      </div>
      <div style='color:#8892a4;font-size:0.85rem;margin-top:0.4rem'>
        {APP_SUBTITLE}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 — EXAMPLE INPUTS EXPANDER
# ─────────────────────────────────────────────────────────────────────────────

with st.expander("💡 Example inputs — click to load", expanded=False):
    if mode == MODE_BUG:
        st.markdown("**Pick a haunted bug to analyse:**")
        cols_ex = st.columns(len(EXAMPLE_BUGS))
        for i, ex in enumerate(EXAMPLE_BUGS):
            if cols_ex[i].button(ex["label"], key=f"ex_bug_{i}"):
                st.session_state.text_area_value = ex["code"]
                st.rerun()

    elif mode == MODE_ALTAR:
        st.markdown("**Pick an example project description:**")
        cols_ex = st.columns(len(EXAMPLE_ALTAR_NOTES))
        for i, ex in enumerate(EXAMPLE_ALTAR_NOTES):
            if cols_ex[i].button(ex["label"], key=f"ex_altar_{i}"):
                st.session_state.text_area_value = ex["note"]
                st.rerun()

    else:
        st.markdown(
            "📸 **Mode 1 — Vision Match:** Upload a photo of your Halloween or "
            "Día de los Muertos costume and optionally add notes."
        )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12 — TWO-COLUMN MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

left_col, right_col = st.columns([1, 1], gap="large")

# ════════════════════════════════════════════════════════════════════
# LEFT COLUMN — "The Séance Table"
# ════════════════════════════════════════════════════════════════════
with left_col:
    st.markdown(
        "<div class='section-label'>🕯️ The Séance Table</div>",
        unsafe_allow_html=True,
    )

    # ── Image input ───────────────────────────────────────────────────────
    image_bytes: Optional[bytes] = None
    image_mime: Optional[str] = None
    pil_preview: Optional[Image.Image] = None

    upload_tab, camera_tab = st.tabs(["📤 Upload", "📸 Live Camera"])

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            image_bytes, image_mime = prepare_image(uploaded_file)
            pil_preview = Image.open(io.BytesIO(image_bytes))

    with camera_tab:
        camera_photo = st.camera_input("Take a photo", label_visibility="collapsed")
        if camera_photo is not None and image_bytes is None:
            image_bytes, image_mime = prepare_image(camera_photo)
            pil_preview = Image.open(io.BytesIO(image_bytes))

    if pil_preview is not None:
        st.image(pil_preview, caption="📷 Image ready for the Oracle", use_container_width=True)

    # ── Text area ─────────────────────────────────────────────────────────
    notes = st.text_area(
        "Notes / code / description",
        value=st.session_state.text_area_value,
        placeholder=PLACEHOLDERS[mode],
        height=200,
        label_visibility="collapsed",
        key="notes_input",
    )

    # Sync session state
    if notes != st.session_state.text_area_value:
        st.session_state.text_area_value = notes

    # ── Mode-specific hints ───────────────────────────────────────────────
    if mode == MODE_VISION and image_bytes is None:
        st.caption("📸 Upload or capture a costume image to begin the Vision Match.")
    elif mode == MODE_BUG and not notes.strip():
        st.caption(
            "🐛 Paste your code or error above (and optionally attach a screenshot)."
        )

    st.markdown("")  # spacer

    # ── Summon button ─────────────────────────────────────────────────────
    summon = st.button("🔮 Summon the Oracle", type="primary", use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — "The Gemma Oracle"
# ════════════════════════════════════════════════════════════════════
with right_col:
    st.markdown(
        "<div class='section-label'>🔮 The Gemma Oracle</div>",
        unsafe_allow_html=True,
    )

    # ── Summon logic ──────────────────────────────────────────────────────
    if summon:
        # ── Resolve API key ───────────────────────────────────────────────
        api_key = get_api_key(sidebar_api_key)
        if not api_key:
            st.warning(
                "🕯️ **The Oracle needs a key to awaken.**\n\n"
                "Please enter your Google AI Studio API key in the sidebar, "
                "or set the `GEMINI_API_KEY` environment variable.\n\n"
                "👉 Get a free key at https://aistudio.google.com/apikey"
            )
            st.stop()

        # ── Validate mode-specific input ──────────────────────────────────
        if mode == MODE_VISION and image_bytes is None:
            st.error(
                "💀 **No costume image detected!**\n\n"
                "The Vision Match Oracle needs an image to read your cosmic fate. "
                "Upload or capture one using the tabs on the left."
            )
            st.stop()

        if mode == MODE_BUG and not notes.strip() and image_bytes is None:
            st.error(
                "🪦 **No bug to bury!**\n\n"
                "Paste your broken code or error message in the text area, "
                "or upload a screenshot of the error. "
                "The Graveyard awaits its next resident."
            )
            st.stop()

        # ── Build prompt & call model ─────────────────────────────────────
        system_prompt = SYSTEM_PROMPTS[mode]
        user_prompt   = build_prompt(mode, notes)
        st.session_state.last_prompt = (
            f"**System prompt:**\n\n```\n{system_prompt}\n```"
            f"\n\n---\n\n**User prompt:**\n\n```\n{user_prompt}\n```"
        )

        spinner_msg = random.choice(SPOOKY_SPINNER_MSGS)
        with st.spinner(spinner_msg):
            try:
                client = get_client(api_key)
                result = call_gemma(
                    client=client,
                    model=active_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    image_bytes=image_bytes,
                    image_mime=image_mime,
                )
                st.session_state.oracle_output   = result
                st.session_state.export_md       = make_markdown_export(mode, active_model, result)
                st.session_state.export_filename = _export_filename(mode)

            except Exception as exc:
                err_str = str(exc)
                err_low = err_str.lower()
                if any(kw in err_low for kw in ("api key", "invalid", "401", "403", "unauthorized")):
                    st.error(
                        "🔑 **Invalid or unauthorized API key.**\n\n"
                        "Check your key at https://aistudio.google.com/apikey"
                    )
                elif any(kw in err_low for kw in ("429", "quota", "rate limit", "resource exhausted")):
                    st.error(
                        "⏳ **Rate limit reached.**\n\n"
                        "The spirits need a moment to recover. "
                        "Wait a minute and try again, or switch to a different model."
                    )
                elif any(kw in err_low for kw in ("not found", "404", "model")):
                    st.error(
                        f"👻 **Model `{active_model}` not found.**\n\n"
                        "Check the model name in the sidebar. "
                        "Available presets: " + ", ".join(f"`{m}`" for m in AVAILABLE_MODELS)
                    )
                elif any(kw in err_low for kw in ("network", "connection", "timeout")):
                    st.error(
                        "🌐 **Network error.**\n\n"
                        "The Oracle's crystal ball lost its signal. "
                        "Check your internet connection and try again."
                    )
                elif any(kw in err_low for kw in ("blocked", "safety")):
                    st.error(
                        f"🛡️ **Safety filter triggered.**\n\n{err_str}\n\n"
                        "Try rephrasing your input."
                    )
                else:
                    st.error(f"💀 **Unexpected Oracle error:**\n\n```\n{err_str}\n```")

    # ── Output display ────────────────────────────────────────────────────
    if st.session_state.oracle_output:
        # Render inside the oracle card using st.markdown for proper MD rendering
        with st.container():
            st.markdown(
                "<div class='oracle-card'>",
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state.oracle_output)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")  # spacer

        # ── Download button ───────────────────────────────────────────────
        st.download_button(
            label="📥 Download Oracle Scroll (.md)",
            data=st.session_state.export_md,
            file_name=st.session_state.export_filename,
            mime="text/markdown",
            use_container_width=True,
        )

        # ── Raw Markdown expander ─────────────────────────────────────────
        with st.expander("📜 Raw Markdown", expanded=False):
            st.code(st.session_state.oracle_output, language="markdown")

        # ── Show prompt expander ──────────────────────────────────────────
        with st.expander("🔬 Show prompt used (open-source transparency)", expanded=False):
            st.markdown(st.session_state.last_prompt)

    else:
        # Placeholder when no output yet
        st.markdown(
            """
            <div class='tombstone-placeholder'>
              <div class='big'>🪦</div>
              <div style='margin-top:0.5rem;font-size:1rem;color:#ff9933'>
                The Oracle Awaits…
              </div>
              <div style='margin-top:0.4rem;font-size:0.82rem'>
                Configure your ritual in the sidebar,<br>
                then summon the Oracle on the left.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 13 — PAGE FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    """
    <div style='text-align:center;color:#8892a4;font-size:0.8rem;padding:0.5rem 0 1.5rem'>
      <span style='color:#ffc107'>🌼</span>
      En el Día de los Muertos, recordamos a quienes nos precedieron
      — los que escribieron el código, enviaron los PRs, y construyeron las comunidades.
      <br>
      <em>On the Day of the Dead, we remember those who came before us
      — those who wrote the code, sent the PRs, and built the communities.</em>
      <br><br>
      🎃 Built with open-source Gemma &nbsp;🧡&nbsp; Hacktoberfest 2026 &nbsp;
      <span style='color:#ffc107'>🌼</span>
    </div>
    """,
    unsafe_allow_html=True,
)
