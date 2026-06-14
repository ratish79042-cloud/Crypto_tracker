from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime

# ── Setup Chrome (headless) ─────────────────────────────────────────────────
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ── Open CoinMarketCap ──────────────────────────────────────────────────────
print("Opening CoinMarketCap...")
driver.get("https://coinmarketcap.com/")
time.sleep(5)

# ── Scrape top-10 rows ──────────────────────────────────────────────────────
rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")[:11]  # grab 11 to account for index row

data = []
timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")

SKIP_COINS = {"CoinMarketCap 20 Index DTF", "CMC200", "CMC Crypto 200"}  # skip index tokens

for row in rows:
    try:
        cols = row.find_elements(By.TAG_NAME, "td")

        name = cols[2].find_element(By.CSS_SELECTOR, "p").text.strip()

        if name in SKIP_COINS:          # skip index row
            continue

        price_raw  = cols[3].text.strip().split("\n")[0]
        price      = "$" + price_raw.replace("$", "").strip()
        change_24h = cols[4].text.strip().split("\n")[0]
        market_cap = cols[6].text.strip().split("\n")[0]

        data.append({
            "Timestamp":   timestamp,
            "Coin Name":   name,
            "Price (USD)": price,
            "24h Change":  change_24h,
            "Market Cap":  market_cap,
        })

        if len(data) == 10:             # stop once we have exactly 10 real coins
            break

    except Exception as e:
        print(f"Skipped a row: {e}")

driver.quit()

# ── Save to CSV ─────────────────────────────────────────────────────────────
if data:
    df = pd.DataFrame(data)
    csv_file = "crypto_prices.csv"

    try:
        existing = pd.read_csv(csv_file)
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv(csv_file, index=False)
    print(f"\n✅ Done! Data saved to '{csv_file}'")
    print(df.to_string(index=False))
else:
    print("❌ No data scraped. The page layout may have changed.")