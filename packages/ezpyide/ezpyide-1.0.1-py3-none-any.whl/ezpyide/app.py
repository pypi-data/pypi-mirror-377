import streamlit as st
from streamlit_ace import st_ace
import subprocess
import os
import json

# ===== Nastavenia =====
SETTINGS_FILE = "ide_settings.json"
DEFAULT_SETTINGS = {
    "theme": "monokai",
    "font_size": 14,
    "keybinding": "vscode",
    "auto_run": False,
    "dark_mode": True
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

settings = load_settings()

st.set_page_config(page_title="Ezpy IDE Web IDE", layout="wide")
st.title("Ezpy IDE – Full Web IDE 🐍")

# ===== BOČNÉ MENU =====
with st.sidebar:
    st.header("🛠 Editor nástroje")
    save_code = st.button("💾 Uložiť kód")
    load_code = st.button("📂 Načítať kód")
    reset_code = st.button("♻️ Reset editor")
    run_code = st.button("▶️ Spusti kód")

    st.markdown("---")
    st.header("⚙️ Nastavenia IDE")
    settings["theme"] = st.selectbox("Vyber tému editora", ["monokai", "github", "solarized_dark", "dracula"], index=["monokai","github","solarized_dark","dracula"].index(settings["theme"]))
    settings["font_size"] = st.slider("Veľkosť písma", min_value=10, max_value=24, value=settings["font_size"])
    settings["keybinding"] = st.selectbox("Keybinding", ["vscode", "emacs", "sublime"], index=["vscode","emacs","sublime"].index(settings["keybinding"]))
    settings["auto_run"] = st.checkbox("Automatické spúšťanie kódu", value=settings["auto_run"])
    settings["dark_mode"] = st.checkbox("Tmavý režim UI", value=settings["dark_mode"])

    if st.button("💾 Uložiť nastavenia"):
        save_settings(settings)
        st.success("Nastavenia uložené ✅")

    st.markdown("---")
    st.header("ℹ️ About")
    st.text("Autor: Denis Varga")
    st.text("Program: Ezpy IDE Web IDE")
    st.text("Verzia: 1.0.0")

# ===== EDITOR =====
user_code = st_ace(
    language="python",
    theme=settings["theme"],
    height=600,
    keybinding=settings["keybinding"],
    font_size=settings["font_size"],
    show_gutter=True,
    wrap=True,
)

# ===== FUNKCIONALITA NÁSTROJOV =====
if save_code:
    with open("saved_code.py", "w", encoding="utf-8") as f:
        f.write(user_code)
    st.success("Kód uložený ✅")

if load_code:
    if os.path.exists("saved_code.py"):
        with open("saved_code.py", "r", encoding="utf-8") as f:
            user_code = f.read()
        st.success("Kód načítaný ✅")
    else:
        st.warning("Žiadny uložený kód")

if reset_code:
    user_code = ""

# ===== SPUSTENIE KÓDU =====
if run_code or settings["auto_run"]:
    if "input(" in user_code or "tkinter" in user_code.lower():
        st.info("Kód obsahuje input() alebo Tkinter – spustím v samostatnej konzole")
        # Ulož kód do dočasného súboru
        with open("temp_run_code.py", "w", encoding="utf-8") as f:
            f.write(user_code)
        # Spusti proces v novom termináli
        if os.name == "nt":  # Windows
            subprocess.Popen(["start", "cmd", "/k", "python", "temp_run_code.py"], shell=True)
        else:  # Linux / Mac
            subprocess.Popen(["x-terminal-emulator", "-e", f"python3 temp_run_code.py"])
        st.success("Kód sa spustí v samostatnej konzole ✅")
    else:
        # Kód bez input(), môžeme spustiť priamo a zobraziť výstup
        import io
        import contextlib
        output = io.StringIO()
        error = io.StringIO()
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                exec(user_code, {})
        except Exception as e:
            error.write(str(e))
        
        st.subheader("Výstup konzoly:")
        konzola = output.getvalue()
        chyba = error.getvalue()
        if konzola:
            st.code(konzola)
        if chyba:
            st.error(chyba)
