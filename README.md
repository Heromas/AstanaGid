# 🏙 Astana City Guide — Telegram Bot

A multilingual Telegram bot that acts as an interactive city guide for **Astana, Kazakhstan**.  
Built with **Python 3.10+** and **aiogram 3.x**, using Finite State Machine (FSM) navigation and Inline keyboards.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🌐 **3 Languages** | Russian 🇷🇺, English 🇬🇧, Kazakh 🇰🇿 — selected at startup, persisted for the session |
| 🗂 **3 Categories** | Active Recreation, Passive Recreation, Eat Out |
| 📍 **12 Places** | 4 real Astana locations per category with descriptions, prices, and 2GIS links |
| 🃏 **Place Cards** | Name · Description · Average bill · Cuisine (food only) · 2GIS map link |
| 🔒 **FSM Navigation** | Clean state machine: Language → Menu → Places → Card → Back |
| 🛡 **Robustness** | All data lookups use safe `.get()` — bot never crashes on missing data |
| 📋 **Logging** | Timestamped logs with level and module name |

---

## 🗂 Project Structure

```
astana-bot/
├── main.py        # Full bot source (single-file)
├── .env           # Your secret token (not committed to git)
├── .env.example   # Template for .env
├── requirements.txt
└── README.md
```

---

## ⚙️ Requirements

```
aiogram>=3.7.0
python-dotenv>=1.0.0
```

Save as `requirements.txt` and install with:

```bash
pip install -r requirements.txt
```

---

## 🚀 Setup & Run

### Step 1 — Get a Bot Token

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts.
3. Copy the token you receive (looks like `123456789:ABCdef...`).

### Step 2 — Configure the token

Create a file named `.env` in the same directory as `main.py`:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

> **Never commit `.env` to version control.**  
> Add it to `.gitignore`: `echo ".env" >> .gitignore`

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the bot

```bash
python main.py
```

You should see:

```
2025-01-01 12:00:00  [INFO]  __main__: ✅ Бот запущен. Нажмите Ctrl+C для остановки.
```

Open Telegram, find your bot, and send `/start`.

---

## 🧭 Bot Navigation Flow

```
/start
  └─► Language selection  (🇷🇺 / 🇬🇧 / 🇰🇿)
        └─► Main Menu
              ├─► 🎯 Active Recreation  → [Khan Shatyr | Formula Karting | ...]
              ├─► 🌿 Passive Recreation → [Baiterek | Central Park | ...]
              └─► 🍽 Eat Out            → [Qazaq Gourmet | Tandyr | ...]
                        └─► Place Card  (name · description · price · cuisine · 2GIS)
                                └─► ◀️ Back to categories
```

---

## 🗄 Adding New Places

Open `main.py` and add an entry to the `places_data` dictionary:

```python
"my_new_place": {
    "name":      {"ru": "...", "en": "...", "kz": "..."},
    "desc":      {"ru": "...", "en": "...", "kz": "..."},
    "avg_check": {"ru": "~X ₸", "en": "~X ₸", "kz": "~X ₸"},
    "cuisine":   {"ru": "...", "en": "...", "kz": "..."},  # food category only; None otherwise
    "gis_url":   "https://2gis.kz/astana/...",
},
```

---

## 🔧 Tech Stack

- **Python 3.10+**
- **aiogram 3.x** — async Telegram Bot API framework
- **FSM (MemoryStorage)** — in-memory state machine per user
- **python-dotenv** — environment variable management

---

## 📝 License

This project is provided for educational purposes.
