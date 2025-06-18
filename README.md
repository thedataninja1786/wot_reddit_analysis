<div align="center">

# World of Tanks Subreddit Data Extraction and Analysis

</div>

<div align="center">
    <img src="WoT.png" alt="WoT" width="96%">
</div>


Love (or hate) World of Tanks and curious about what the community is talking about? This repo is your all-in-one toolkit for diving deep into the subreddits' discussions, featuring an ETL pipeline and smart AI analysis. Whether you want to track trends, analyze sentiment, or just geek out over tank talk, this repo helps you turn chatter into meaningful insights—because games (and their communities) deserve great data!

- **Post ETL**: Extract posts from the World of Tanks subreddit, transform, and load into PostgreSQL.
- **Comment ETL**: Extract comments from posts.
- **AI Analysis**: Use an AI model to categorize and reason about posts.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Environment Variables](#environment-variables)
4. [Project Structure](#project-structure)
5. [Database Schema](#database-schema)
6. [Usage](#usage)
   - [Run Full Pipeline (``main.py``)](#run-full-pipeline-mainpy)
   - [Run Individual ETL Tasks](#run-individual-etl-tasks)
   - [Run AI Analysis](#run-ai-analysis)
7. [Module Details](#module-details)
8. [Testing & Linting](#testing--linting)
9. [Contributing](#contributing)
10. [License](#license)

---

## Prerequisites

- Python 3.10+ (tested on 3.11)
- PostgreSQL database
- Virtual environment tool (e.g., `venv`)
- Valid Reddit API credentials (via [PRAW](https://praw.readthedocs.io/))
- OpenAI API key

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thedataninja1786/wot_reddit_analysis.git wot_reddit_data
   cd wot_reddit_data
   ```
2. **Create and activate a virtual environment**

    - **Windows (PowerShell):**
      ```powershell
      python -m venv venv
      .\venv\Scripts\Activate
      ```

    - **macOS/Linux (bash/zsh):**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database schema**
   ```bash
   psql -h <host> -p <port> -U <user> -d <dbname> -f data_model/schema.sql
   ```

## Environment Variables

Create a `.env` file in the project root with the following entries:

```dotenv
# PostgreSQL credentials
db_user=<your_db_user>
db_password=<your_db_password>
db_host=<your_db_host>
db_port=<your_db_port>
db_name=<your_db_name>

# Reddit API credentials
user_name=<your_reddit_username>
client_id=<reddit_client_id>
client_secret=<reddit_client_secret>
user_agent=script:WorldOfTanksETL:1.0 (by u/<your_username>)

# OpenAI API key
API_KEY=<your_openai_api_key>
```


## Project Structure

```
wot_reddit_data/
├── ai_moderator/              # AI categorization logic
│   ├── chatbot.py             # AIModerator class for OpenAI calls
│   └── analyze_posts.py       # PostAnalyzer for streaming AI analysis
├── api/                       # Configuration for API credentials and schemas
│   └── configs.py
├── data_model/                # Database schema and data definitions
│   └── schema.sql
├── dataloader/                # Database connectivity and loader
│   └── load_data.py           # DataLoader for read/write operations
├── etl/                       # ETL pipeline scripts
│   ├── extract_load_posts.py  # Post extraction & load
│   ├── extract_load_comments.py # Comment extraction & load
│   └── ai_analysis.py         # High-level AI analysis orchestration
├── extractors/                # Lower-level extraction utilities
│   ├── extract_posts.py
│   └── extract_posts_comments.py
├── utils/                     # Utility functions
│   └── utilities.py           # e.g., get_env_variable, logging setup
├── main.py                    # Single entry point for full pipeline
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
```

## Database Schema

- **POSTS**: Stores Reddit post metadata.
- **COMMENTS**: Nested comment data with `post_id` foreign key to `POSTS`.
- **POSTS_AI_ANALYSIS**: AI categorization results, foreign keyed to `POSTS`.

See `data_model/schema.sql` for full DDL.

## Usage

### Run Full Pipeline (`main.py`)

```bash
python main.py
```
- Executes: `etl_posts()`, `analyze_posts()`, then `etl_comments()`.

### Run Individual ETL Tasks

- **Extract & Load Posts**:
  ```bash
  python -m etl.extract_load_posts
  ```

- **Extract & Load Comments**:
  ```bash
  python -m etl.extract_load_comments
  ```

### Run AI Analysis Only

```bash
python -m etl.ai_analysis
```
- Discovers new posts, calls OpenAI, and upserts into `posts_ai_analysis`.

## Module Details

- **etl.extract_load_posts**: Connects to Reddit via PRAW, fetches posts, and loads into `POSTS` table.
- **etl.extract_load_comments**: Recursively unnests Reddit comments, transforms, and loads into `COMMENTS`.
- **etl.ai_analysis**: Orchestrates AI categorization of new posts, writing results to `POSTS_AI_ANALYSIS`.
- **ai_moderator.chatbot**: Defines `AIModerator` class that wraps OpenAI calls.
- **ai_moderator.analyze_posts**: Defines `PostAnalyzer` for streaming sentiment analysis with error handling.
- **dataloader.load_data**: `DataLoader` class for read/write operations (supports upsert).
- **api.configs**: Configuration classes for table mappings and API defaults.
- **utils.utilities**: Helper functions (e.g., `get_env_variable`).

## Testing & Linting

- **Lint**: `flake8` (configured in `setup.cfg` if present).
- **Format**: `black .`

## CI/CD and Automated Workflows

This project uses GitHub Actions to automate the ETL pipeline on a schedule:

- Workflow file: `.github/workflows/scheduled_etl.yml`
- Runs `main.py` every 8 hours (at 00:00, 08:00, and 16:00 UTC) to keep data up to date.

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes with clear messages
4. Open a pull request
