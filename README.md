# 🎮 GamerMacro Pro — Nebula UI

Aplicatie desktop de automatizare cu detectie de pixeli, cu interfata moderna
(gradient mov-grafit, glassmorphism) construita peste un motor de automatizare
testat separat de UI.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
![UI](https://img.shields.io/badge/UI-pywebview-8b5cf6?style=flat-square)

## ⬇️ Download EXE
👉 **[Descarca GamerMacroPro.exe](../../releases/latest)**

## ✨ Ce contine

**🎣 Macro** — detectorul principal (pescuit): pozitie + culoare + toleranta,
delay de reactie, cooldown, recalibrare pe timeout, pixel-wait, mod natural
(8% skip), Slugfish (asteapta X secunde de la ultima aruncare inainte sa
reactioneze la musca — hookset intarziat, deliberat).

**❄️ Winter** — recunoaste dupa culoare ce creatura marina a aparut la
pescuit (Grinch / Nutcracker, pixel picker cu numaratoare de 3 secunde,
acelasi design ca la Macro) si lupta automat: Grinch primeste click stanga
pana dispare; Nutcracker primeste cicluri de foc (tasta+click dreapta)
urmat imediat de sabie (tasta+click stanga in bucla), cronometrate de la
activarea focului, pana moare sau se atinge un plafon de siguranta de
cicluri. Cat dureaza o lupta, Macro se pune automat pe pauza (nu incearca
sa recasteze in acelasi timp) si reia singur dupa.

**🗂️ Profile** — salveaza/incarca toata configuratia (Macro + Winter)
sub un nume, stocate in `~/.gamermacro/profiles/`.

**📊 Statistici** — catches, recalibrari, skip-uri, Grinch/Nutcracker
ucisi, runtime live pentru fiecare sistem.

**📋 Log** — feed live color-codat, filtrabil pe Macro/Winter.

## 🖥️ Arhitectura

```
gm/engine.py     motorul de automatizare — fara UI, testat cu unittest
                 (FishingWorker, SeaWorker + configurile lor)
app.py           bridge Python <-> UI (pywebview), expune API-ul catre JS
ui/              interfata (HTML/CSS/JS), randata ca fereastra nativa
tests/           teste pentru gm/engine.py (python -m unittest -v)
legacy/          versiunile tkinter anterioare, pastrate ca referinta
```

Motorul (`gm/engine.py`) nu stie nimic despre UI — poate fi testat cu un
backend fals (`NullBackend`/fake), iar interfata (pywebview) doar trimite
configuratii si citeste evenimente live dintr-o coada thread-safe. Asta
inseamna ca UI-ul se poate schimba complet (cum s-a intamplat aici) fara sa
se atinga logica de automatizare.

## 🚀 Rulare manuala

```bash
pip install -r requirements.txt
python app.py
```

## 🔨 Build executabil

```bash
# Windows
build.bat

# Linux/macOS
./build.sh
```

Rezultat: `dist/GamerMacroPro.exe` (onefile, fara consola).

## 🧪 Teste

```bash
python -m unittest discover -s tests -v
```
