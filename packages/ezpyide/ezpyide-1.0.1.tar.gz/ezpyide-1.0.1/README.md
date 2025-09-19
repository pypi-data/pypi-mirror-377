
# EZPy – Python Web IDE 🐍

EZPy je jednoduché a moderné **Python Web IDE** postavené na **Streamlit** a **Streamlit Ace editori**.  
Umožňuje písať, spúšťať a ukladať Python kód priamo vo webovom prostredí na vašom PC.

---

## Funkcie

- Interaktívny **ACE editor** s podporou tém, fontov a keybindingov (`vscode`, `emacs`, `sublime`)
- **Ukladanie a načítanie kódu**
- **Spúšťanie kódu** priamo v appke, vrátane podpory `input()` a Tkinter v samostatnej konzole
- **Nastavenia IDE**: témy, font size, tmavý režim, automatické spúšťanie kódu
- Sidebar s informáciami o verzii a autorovi

---

## Inštalácia

###  inštalácia


```bash
pip install ezpyide
````

### Spustenie

```bash
python -m ezpyide
```

* Alebo priamo:

```bash
ezpyide
```

* Otvorí sa Streamlit server a webové rozhranie EZPy IDE v prehliadači.

---

## Štruktúra projektu


ezpy/
│
├── ezpy/              # hlavný modul balíka
│   ├── __init__.py    # import run alebo prázdny
│   ├── __main__.py    # spustiteľný modul pre python -m ezpy
│   └── app.py         # Streamlit appka
│
├── setup.py           # inštalačný skript
└── README.md


---

## Požiadavky (automaticky sa ninstaluje s ide)

* Python >= 3.8
* [Streamlit](https://streamlit.io/)
* [streamlit-ace](https://github.com/andfanilo/streamlit-ace)

```bash
pip install streamlit streamlit-ace
```

---

## Použitie

1. Napíš kód do editora
2. Ulož alebo načítaj kód pomocou sidebar tlačidiel
3. Spusti kód kliknutím na **▶️ Spusti kód** alebo nastav **Automatické spúšťanie**
4. Sleduj výstup priamo v appke

---

## Autor

**Denis Varga** – tvorca EZPy IDE

---

## Verzia

1.0.0



