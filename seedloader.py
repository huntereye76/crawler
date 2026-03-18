from playwright.sync_api import sync_playwright
import urllib.parse
import re
import psycopg2
import time
import random
import os
from keywords import keywords

# ==============================
# SETTINGS
# ==============================

EXPORT_TXT = True
SAVE_TO_DB = True

DB_URL = "postgresql://neondb_owner:npg_O8yn7oWlKCZM@ep-shy-brook-a109nwqt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

PAGES_PER_KEYWORD = 3
BATCH_SIZE = 3

PROGRESS_FILE = "progress.txt"

# ==============================
# PROGRESS HANDLING
# ==============================

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f:
            f.write("0")
        return 0
    try:
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_progress(index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

# ==============================
# SAVE FUNCTION
# ==============================

def save_links(links):
    if not links:
        return

    if SAVE_TO_DB:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        for link in links:
            cur.execute("""
                INSERT INTO crawl_queue (url, status)
                VALUES (%s, 'pending')
                ON CONFLICT (url) DO NOTHING
            """, (link,))

        conn.commit()
        cur.close()
        conn.close()

    if EXPORT_TXT:
        with open("telegram_groups.txt", "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")

# ==============================
# REGEX (FAST)
# ==============================

TG_REGEX = re.compile(r"https://t\.me/[A-Za-z0-9_]+")

# def extract_links(html):
    # links = set()

    # # 1. encoded links
    # matches = re.findall(r"uddg=([^&]+)", html)
    # for encoded_url in matches:
        # decoded = urllib.parse.unquote(encoded_url)
        # if "t.me/" in decoded:
            # links.add(decoded)

    # # 2. direct links (backup)
    # direct = re.findall(r"https://t\.me/[A-Za-z0-9_]+", html)
    # links.update(direct)

    # return list(set([
        # link for link in links
        # if link.count("/") == 3 and "+" not in link and "joinchat" not in link
    # ]))

# ==============================
# MAIN SCRIPT
# ==============================

found_links = set()
start_index = load_progress()

print(f"Starting from keyword index: {start_index}")

with sync_playwright() as p:

    for i in range(start_index, len(keywords), BATCH_SIZE):

        batch = keywords[i:i+BATCH_SIZE]
        print(f"\n🚀 Processing batch {i} → {i + len(batch)}")

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 🔥 Block unnecessary resources
        page.route("**/*", lambda route: route.abort()
                   if route.request.resource_type in ["image", "stylesheet", "font", "media"]
                   else route.continue_())

        for keyword in batch:

            print(f"\nKeyword: {keyword}")

            for page_no in range(PAGES_PER_KEYWORD):

                start = page_no * 10
                query = f"site:t.me {keyword}"
                url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&s={start}"

                print("Searching:", url)

                try:
                    page.goto(url, timeout=30000)
                    
                    # wait for real results (IMPORTANT FIX)
                    page.wait_for_selector('a[data-testid="result-title-a"]', timeout=10000)

                    elements = page.query_selector_all('a[data-testid="result-title-a"]')

                    new_links = []

                    for el in elements:
                        link = el.get_attribute("href")

                        if link and "t.me/" in link:
                            if link.count("/") == 3 and "+" not in link and "joinchat" not in link:

                                if link not in found_links:
                                    found_links.add(link)
                                    new_links.append(link)
                                    
                                    
                    # elements = page.query_selector_all('a[data-testid="result-title-a"]')

                    # print("\n--- ALL LINKS ON THIS PAGE ---")

                    # new_links = []

                    # for el in elements:
                        # link = el.get_attribute("href")

                        # print(link)   # 👈 DEBUG LINE (ADD THIS)

                        # if link and "t.me/" in link:
                            # if link.count("/") == 3 and "+" not in link and "joinchat" not in link:

                                # if link not in found_links:
                                    # found_links.add(link)
                                    # new_links.append(link)                
                                    
                                    
                                    
                    # print("Found:", len(new_links), "new links")  #temp
                    print("Total on page:", len(elements))

                    # 🛡️ Anti-block delay
                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print("Error:", e)

        # 💾 SAVE AFTER EACH BATCH
        print("\n💾 Saving batch data...")
        save_links(found_links)
        print(f"Saved {len(found_links)} links")

        found_links.clear()

        # 🔄 SAVE PROGRESS
        save_progress(i + BATCH_SIZE)

        # 🔁 Restart browser
        browser.close()

print("\n✅ Done")
