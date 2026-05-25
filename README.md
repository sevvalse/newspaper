# AI-Powered Daily News📰

An automated backend pipeline that tracks multiple news RSS feeds throughout the day, scrapes clean article contents, uses AI to strip away clickbait and filler, and delivers a rafine, ad-free digital newspaper straight to your inbox every evening.

## Features
- **Multi-Source RSS Tracking:** Periodically monitors chosen news outlets without dealing with their heavy UI or ads.
- **Clean Content Scraping:** Extracts the core article body text, automatically bypassing sidebars, popups, and cookie banners.
- **AI-Powered Synthesizing:** Uses the OpenAI API to distill the 5Ws & 1H, key figures, and crucial quotes from the day's events.
- **De-duplication & Clustering:** Automatically groups similar news stories together to avoid redundant updates.
- **Production-Ready Storage:** Built on top of PostgreSQL with a structured pipeline state tracking.

---

## Tech Stack
- **Language:** Python 3.10+
- **Database:** PostgreSQL
- **Parsing & Scraping:** `feedparser`, `newspaper3k`
- **AI Engine:** OpenAI API
- **Templating:** `Jinja2` (HTML/CSS Mail Template)
- **Automation:** Python `schedule` / `cron`

---

## System Architecture

1. **Scrape:** Cron job triggers the RSS Scraper 3 times a day.
2. **Store:** Unique articles are filtered and saved into the PostgreSQL database.
3. **Process:** Evening script pulls all unprocessed text from the database.
4. **Synthesize:** AI processes raw text into bullet-point summaries and extracts key quotes.
5. **Deliver:** SMTP client compiles the HTML template and dispatches the newsletter.
