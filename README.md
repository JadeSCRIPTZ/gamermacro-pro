# 🎮 GamerMacro Pro

Un tool complet de automatizare pentru gameri — inregistreaza taste si click-uri, reda-le cu viteza variabila si detecteaza pixeli pe ecran.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ⬇️ Download direct (fara Python)

👉 **[Descarca GamerMacroPro.exe](../../releases/latest)**

Dublu-click si gata — nu trebuie sa instalezi nimic.

---

## ✨ Features

### ⏺ Tab 1 — Macro Recorder
- **Inregistreaza** orice combinatie de taste si click-uri mouse
- **Redeaza** cu viteza variabila (0.5x, 1x, 2x, etc.)
- **Loop** de N ori sau infinit
- **Salveaza / Incarca** profiluri `.json`
- Tasta de oprire configurabila (default: F8)

### 👁 Tab 2 — Pixel Watcher
- **Monitorizeaza** un pixel specific pe ecran
- Detecteaza schimbarea culorii cu **toleranta ajustabila**
- Executa actiuni predefinite:
  - Right-click x2 (Minecraft fishing)
  - Left-click x1 / x2
  - Apasa tasta E sau F
- **State machine** inteligent — nu triggereaza de doua ori pe acelasi eveniment
- Cooldown configurabil dupa fiecare actiune

---

## 🚀 Instalare manuala (cu Python)

```bash
git clone https://github.com/JadeSCRIPTZ/gamermacro-pro.git
cd gamermacro-pro
pip install -r requirements.txt
python gamermacro.py
```

---

## 📖 Cum folosesti Macro Recorder

1. Du-te in joc, apasa **⏺ RECORD**
2. Executa actiunile pe care vrei sa le inregistrezi
3. Apasa **⏹ STOP REC**
4. Seteaza viteza si numarul de bucle
5. Apasa **▶ PLAY**
6. Salveaza profilul cu **💾 Salveaza** pentru a-l folosi data viitoare

## 📖 Cum folosesti Pixel Watcher

1. Apasa **🖱 Get Mouse Position** — ai 3 secunde sa misti mouse-ul pe pixelul tinta
2. Apasa **🎨 Get Colour Under Mouse** — citeste culoarea pixelului
3. Ajusteaza toleranta (default: ±15)
4. Alege actiunea din lista
5. Apasa **▶ START WATCHER**

---

## ⚠️ Oprire urgenta

Muta mouse-ul in **coltul stanga-sus** al ecranului — PyAutoGUI FailSafe opreste totul instant.

---

## 📦 Dependente

| Pachet | Scop |
|--------|------|
| `pyautogui` | Click-uri mouse si detectie pixeli |
| `pynput` | Captare taste si click-uri la inregistrare |
| `pillow` | Screenshot support |
| `tkinter` | GUI (inclus in Python) |

---

## 📄 Licenta

MIT — liber de folosit si modificat.
