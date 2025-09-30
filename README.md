Here’s the English translation of your text:

---

# Perfume Bot MVP

A bot for searching perfumes and their popular clones, including savings calculation.

**Key update:** The project has been migrated to **PostgreSQL** for cloud deployment (e.g., Render) and a logging system for all user messages has been added for analytics.

---

## 📂 Project Structure

```
perfume-bot/
│
├── web.py         # Launch and Telegram handlers, including request logging
├── database.py    # PostgreSQL operations and table initialization 👈
├── search.py      # Parsing and flexible search logic (brand/name, fuzzy)
├── formatter.py   # Building nicely formatted response text
├── followup.py    # "Hooray! 🎉..." logic (sent once)
├── utils.py       # Text normalization, transliteration
├── i18n.py        # File for localization of all string constants
├── analyze_db.py  # Script for deep analytics of data and user behavior
├── requirements.txt
└── .env
```

---

## 🗄️ Database Structure (PostgreSQL)

The database consists of **three** main tables:

### 1. `UserMessages` Table (Logging)

Stores all user queries for analytics and error tracking.

| Column      | Data Type                  | Description                                        |
| ----------- | -------------------------- | -------------------------------------------------- |
| `id`        | `SERIAL PRIMARY KEY`       | Unique ID                                          |
| `user_id`   | `BIGINT`                   | Telegram user ID                                   |
| `timestamp` | `TIMESTAMP WITH TIME ZONE` | Message timestamp                                  |
| `message`   | `TEXT`                     | Original message text                              |
| `status`    | `TEXT`                     | Status (e.g., `success`, `fail`, `start_command`)  |
| `notes`     | `TEXT`                     | Additional notes (e.g., Fuzzy Match, error reason) |

### 2. `OriginalPerfume` Table (Originals)

Stores information about expensive original perfumes.

| Column      | Data Type          | Description                   |
| ----------- | ------------------ | ----------------------------- |
| `id`        | `TEXT PRIMARY KEY` | Unique ID (Primary Key)       |
| `brand`     | `TEXT`             | Original brand                |
| `name`      | `TEXT`             | Original name                 |
| `price_eur` | `REAL`             | Price in euros                |
| `url`       | `TEXT`             | Link to original product page |

### 3. `CopyPerfume` Table (Clones/Alternatives)

Stores information about perfume clones linked to originals.

| Column         | Data Type          | Description                                                              |
| -------------- | ------------------ | ------------------------------------------------------------------------ |
| `id`           | `TEXT PRIMARY KEY` | Unique ID (Primary Key)                                                  |
| `original_id`  | `TEXT`             | Link to `id` in `OriginalPerfume` (`FOREIGN KEY`)                        |
| `brand`        | `TEXT`             | Clone brand                                                              |
| `name`         | `TEXT`             | Clone name                                                               |
| `price_eur`    | `REAL`             | Clone price in euros                                                     |
| `url`          | `TEXT`             | Link to clone                                                            |
| `notes`        | `TEXT`             | Notes about the fragrance                                                |
| `saved_amount` | `REAL`             | Savings in %: `(orig_price_eur - dupe_price_eur) / orig_price_eur * 100` |

---

## 🚀 Running the Project

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
   Create a `.env` file in the root directory and define **all** required variables.

```
# --- BOT SETTINGS ---
BOT_TOKEN="YOUR_TOKEN_HERE"
WEBHOOK_URL="YOUR_WEBHOOK_URL_ON_RENDER"
# Optional: Bot language (ru or en). Default is ru.
BOT_LANG="ru"

# --- POSTGRESQL SETTINGS ---
# Variable used by Render
DATABASE_URL="postgresql://perfume_bot_public_posgresql_user:kIlMPx2gsC9uACxwMMk5KckZ4WaOsWit@dpg-d3c11k2li9vc73d6lee0-a/perfume_bot_public_posgresql"
```

3. **Run the bot:**
   For webhook deployment on Render, you’ll likely need `gunicorn` or another WSGI server.

```bash
gunicorn web:app
```

---

## 🔬 Database Analytics

Use **`analytics.py`** for quick access to key data.

1. **Ensure `DATABASE_URL` is set** (see above).
2. **Run the script:**

```bash
python3 analytics.py
```

The script outputs:

* Total number of Originals and Clones
* 5 most recently added perfumes
* 5 clones with the highest savings
* Overall user query statistics (`success`, `fail`, `start_command`)
* 10 most recent **failed** queries for analysis (not found by the bot)
* 10 most recent **successful but imprecise** queries (Fuzzy Match)

---

If you want, I can also produce a **clean, fully formatted README in English** ready for GitHub. It would look more professional and readable. Do you want me to do that?
