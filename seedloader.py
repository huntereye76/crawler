# from playwright.sync_api import sync_playwright
# import urllib.parse
# import re
# import psycopg2
# import time
# import random
# import os
# from keywords import keywords

# # ==============================
# # SETTINGS
# # ==============================

# EXPORT_TXT = False
# SAVE_TO_DB = True

# DB_URL = "postgresql://neondb_owner:npg_O8yn7oWlKCZM@ep-shy-brook-a109nwqt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# PAGES_PER_KEYWORD = 3
# BATCH_SIZE = 3

# PROGRESS_FILE = "progress.txt"

# # ==============================
# # PROGRESS HANDLING
# # ==============================

# def load_progress():
#     if not os.path.exists(PROGRESS_FILE):
#         with open(PROGRESS_FILE, "w") as f:
#             f.write("0")
#         return 0
#     try:
#         with open(PROGRESS_FILE, "r") as f:
#             return int(f.read().strip())
#     except:
#         return 0

# def save_progress(index):
#     with open(PROGRESS_FILE, "w") as f:
#         f.write(str(index))

# # ==============================
# # SAVE FUNCTION
# # ==============================

# def save_links(links):
#     if not links:
#         return

#     if SAVE_TO_DB:
#         conn = psycopg2.connect(DB_URL)
#         cur = conn.cursor()

#         for link in links:
#             cur.execute("""
#                 INSERT INTO crawl_queue (url, status)
#                 VALUES (%s, 'pending')
#                 ON CONFLICT (url) DO NOTHING
#             """, (link,))

#         conn.commit()
#         cur.close()
#         conn.close()

#     if EXPORT_TXT:
#         with open("telegram_groups.txt", "a", encoding="utf-8") as f:
#             for link in links:
#                 f.write(link + "\n")

# # ==============================
# # REGEX (FAST)
# # ==============================

# TG_REGEX = re.compile(r"https://t\.me/[A-Za-z0-9_]+")

# # def extract_links(html):
#     # links = set()

#     # # 1. encoded links
#     # matches = re.findall(r"uddg=([^&]+)", html)
#     # for encoded_url in matches:
#         # decoded = urllib.parse.unquote(encoded_url)
#         # if "t.me/" in decoded:
#             # links.add(decoded)

#     # # 2. direct links (backup)
#     # direct = re.findall(r"https://t\.me/[A-Za-z0-9_]+", html)
#     # links.update(direct)

#     # return list(set([
#         # link for link in links
#         # if link.count("/") == 3 and "+" not in link and "joinchat" not in link
#     # ]))

# # ==============================
# # MAIN SCRIPT
# # ==============================

# found_links = set()
# start_index = load_progress()

# print(f"Starting from keyword index: {start_index}")

# with sync_playwright() as p:

#     for i in range(start_index, len(keywords), BATCH_SIZE):

#         batch = keywords[i:i+BATCH_SIZE]
#         print(f"\n🚀 Processing batch {i} → {i + len(batch)}")

#         #browser = p.chromium.launch(headless=True)
#         browser = p.chromium.launch(
#             headless=True,
#             args=["--no-sandbox", "--disable-dev-shm-usage"]
#         )
        
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
#             viewport={"width": 1280, "height": 800}
#         )
        
#         page = context.new_page()

#         # 🔥 Block unnecessary resources
#         page.route("**/*", lambda route: route.abort()
#                    if route.request.resource_type in ["image", "font", "media"]
#                    else route.continue_())

#         for keyword in batch:

#             print(f"\nKeyword: {keyword}")

#             for page_no in range(PAGES_PER_KEYWORD):

#                 start = page_no * 10
#                 query = f"site:t.me {keyword}"
#                 # url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&s={start}"
#                 url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}&s={start}"

#                 print("Searching:", url)

#                 elements = []
                
#                 for attempt in range(3):
#                     try:
#                         page.goto(url, timeout=30000)
                
#                         page.wait_for_timeout(3000)
                
#                         page.wait_for_selector('a[href*="t.me"]', timeout=15000)
                
#                         elements = page.query_selector_all('a[href*="t.me"]')
                
#                         break
                
#                     except Exception as e:
#                         print(f"Retry {attempt+1} failed:", e)
                
#                         if attempt == 2:
#                             print("Skipping this page...")
                
#                 # ✅ OUTSIDE retry loop
#                 new_links = []
                
#                 for el in elements:
#                     link = el.get_attribute("href")
                
#                     if link and "t.me/" in link:
#                         if link.count("/") == 3 and "+" not in link and "joinchat" not in link:
                
#                             if link not in found_links:
#                                 found_links.add(link)
#                                 new_links.append(link)
                
#                 print("Total on page:", len(elements))
                
#                 time.sleep(random.uniform(1, 3))
                                    
                                    
                                    
                 

#         # 💾 SAVE AFTER EACH BATCH
#         print("\n💾 Saving batch data...")
#         save_links(found_links)
#         print(f"Saved {len(found_links)} links")

#         found_links.clear()

#         # 🔄 SAVE PROGRESS
#         save_progress(i + BATCH_SIZE)

#         # 🔁 Restart browser
#         browser.close()

# print("\n✅ Done")




from playwright.sync_api import sync_playwright
from playwright_stealth import stealth# NEW: Added stealth
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
EXPORT_TXT = False
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
        try:
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
        except Exception as e:
            print(f"DB Error: {e}")

    if EXPORT_TXT:
        with open("telegram_groups.txt", "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")

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

        # NEW: Added '--headless=new' and stealth features
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        stealth(page)  # NEW: Apply stealth to this page

        # Block unnecessary resources (careful: blocking too much can trigger bot detection)
        page.route("**/*", lambda route: route.abort()
                   if route.request.resource_type in ["font", "media"] # Keep images for better human-like behavior
                   else route.continue_())

        for keyword in batch:
            print(f"\nKeyword: {keyword}")

            for page_no in range(PAGES_PER_KEYWORD):
                start = page_no * 10
                query = f"site:t.me {keyword}"
                # NEW: Using main URL instead of /html/ which is more prone to IP blocks
                url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&s={start}&df=y"

                print("Searching:", url)
                elements = []
                
                for attempt in range(3):
                    try:
                        # Add a small delay before navigating
                        time.sleep(random.uniform(2, 4))
                        
                        page.goto(url, timeout=45000, wait_until="domcontentloaded")
                        
                        # Wait for the results container (DuckDuckGo uses 'react-layout-main' or similar)
                        # Instead of just the link, we wait for the page to load
                        page.wait_for_selector('div.react-results--main', timeout=20000)
                        
                        # Find all t.me links
                        elements = page.query_selector_all('a[href*="t.me"]')
                        break
                
                    except Exception as e:
                        print(f"Retry {attempt+1} failed. Potential block or timeout.")
                        if attempt == 2:
                            # Save a screenshot for debugging
                            page.screenshot(path=f"error_keyword_{i}.png")
                            print("Skipping this page...")

                new_links = []
                for el in elements:
                    try:
                        link = el.get_attribute("href")
                        # Handle DDG proxy links (extract the t.me part)
                        if link and "t.me/" in link:
                            # Clean the URL if it's wrapped in a DDG redirect
                            if "uddg=" in link:
                                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                            
                            if link.count("/") == 3 and "+" not in link and "joinchat" not in link:
                                if link not in found_links:
                                    found_links.add(link)
                                    new_links.append(link)
                    except:
                        continue
                
                print(f"Found {len(new_links)} new links on this page.")
                time.sleep(random.uniform(3, 6)) # More human-like pause

        # 💾 SAVE AFTER EACH BATCH
        print("\n💾 Saving batch data...")
        save_links(found_links)
        print(f"Saved total {len(found_links)} links for this batch")
        found_links.clear()

        # 🔄 SAVE PROGRESS
        save_progress(i + BATCH_SIZE)
        browser.close()

print("\n✅ Done")
