### 📖 About the Project

**Perfume Twins** helps users discover affordable alternatives to expensive original perfumes. By querying the bot, users can find "dupes" or clones that match the scent profile of luxury brands, complete with price comparisons and direct purchase links.

### 📱 Bot Preview

These screenshots show the main user flow: opening the bot, browsing popular fragrances, and finding affordable alternatives for a specific scent.

#### 1. Main Menu

Users start from a simple menu with the core actions: search, popular picks, history, and language switching.

![Main menu of the Perfume Twins Telegram bot](assets/screenshots/main-menu.jpg)

#### 2. Popular Fragrances

The bot can surface the most frequently requested fragrances, which makes exploration easier for first-time users.

![Popular fragrances list in the Perfume Twins Telegram bot](assets/screenshots/popular-fragrances.jpg)

#### 3. Search Results

After entering a perfume name, users receive a list of cheaper alternatives with direct purchase links.

![Search results with perfume dupes in the Perfume Twins Telegram bot](assets/screenshots/search-results.jpg)

### 📂 Project Structure

The codebase is organized as a modular Python application using Flask (via `web.py`) for webhook handling.

```text
perfume-bot/
├── web.py            # Entry point: FastAPI/Flask app & Webhook handler
├── search.py         # Core logic: Search algorithms for matching perfumes
├── database.py       # ORM & Database connection management
├── formatter.py      # UI: Formats text responses for Telegram
├── followup.py       # Logic: Handles conversation flow and user context
├── i18n.py           # Localization: Language handling
├── analyze_db.py     # Analytics: Script to generate DB statistics
├── utils.py          # Helper functions
├── requirements.txt  # Python dependencies
└── .env              # Environment variables (Configuration)

```

---

### 🗄️ Database Schema

The project uses PostgreSQL. Below is the schema design for tracking users and mapping perfume relationships.

#### 1. UserMessages (`UserMessages`)

*Stores interaction logs for analytics and debugging.*

| Column | Type | Description |
| --- | --- | --- |
| `id` | `SERIAL PK` | Unique Log ID |
| `user_id` | `BIGINT` | Telegram User ID |
| `timestamp` | `TIMESTAMP` | Time of message receipt |
| `message` | `TEXT` | Raw text sent by user |
| `status` | `TEXT` | Query outcome (e.g., `success`, `fail`) |
| `notes` | `TEXT` | Debugging info or errors |

#### 2. Original Perfumes (`OriginalPerfume`)

*Catalog of luxury/reference fragrances.*

| Column | Type | Description |
| --- | --- | --- |
| `id` | `TEXT PK` | Unique SKU/ID |
| `brand` | `TEXT` | Brand Name (e.g., "Tom Ford") |
| `name` | `TEXT` | Perfume Name (e.g., "Tobacco Vanille") |
| `price_eur` | `REAL` | Market Price (€) |
| `url` | `TEXT` | Link to official product page |

#### 3. Clones / Alternatives (`CopyPerfume`)

*Budget-friendly alternatives linked to originals.*

| Column | Type | Description |
| --- | --- | --- |
| `id` | `TEXT PK` | Unique SKU/ID |
| `original_id` | `TEXT` | **FK** linking to `OriginalPerfume.id` |
| `brand` | `TEXT` | Clone Brand (e.g., "Lattafa") |
| `name` | `TEXT` | Clone Name |
| `price_eur` | `REAL` | Market Price (€) |
| `saved_amount` | `REAL` | Calculated savings %: `(orig - dupe) / orig * 100` |
| `url` | `TEXT` | Link to purchase |
| `notes` | `TEXT` | Scent notes or specific differences |

---

### 🚀 Installation & Setup

**Prerequisites:** Python 3.9+, PostgreSQL.

**1. Install Dependencies**

```bash
pip install -r requirements.txt

```

**2. Configuration**
Create a `.env` file in the root directory:

```ini
# Telegram API
BOTTOKEN="your_telegram_bot_token"
WEBHOOKURL="https://your-domain.com/webhook"
BOT_LANG="ru" 

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

```

**3. Run the Bot**
Use Gunicorn to serve the application in production:

```bash
gunicorn web:app

```

---

### 📊 Analytics

Run the analytics script to view database health and user query performance.

```bash
python3 analyze_db.py

```

**Output Includes:**

* **Inventory:** Total count of Originals vs. Clones.
* **Recents:** 5 most recently added perfumes.
* **Top Savers:** 5 clones offering the highest percentage savings.
* **Performance:** Query stats (`success` vs `fail` rates).
* **Misses:** Last 10 failed queries (useful for filling DB gaps).
* **Fuzzy Logic:** Last 10 fuzzy matches (to check search accuracy).
