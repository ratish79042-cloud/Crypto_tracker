from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://coinmarketcap.com/")
time.sleep(5)

rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")[:15]
data = []
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for row in rows:
    try:
        cols = row.find_elements(By.TAG_NAME, "td")
        name = cols[2].find_element(By.CSS_SELECTOR, "p").text.strip()

        # ✅ Skip non-coin rows, Start from Bitcoin
        if name in {"CoinMarketCap 20 Index DTF", "CMC200"} or (not data and name != "Bitcoin"):
            continue

        price      = cols[3].text.strip().split("\n")[0]
        change_24h = cols[4].text.strip().split("\n")[0]
        market_cap = next((cols[i].text.strip().split("\n")[0] for i in range(5, len(cols)) if cols[i].text.strip().startswith("$") and len(cols[i].text.strip()) > 5), "")

        data.append({"Timestamp": timestamp, "Coin Name": name, "Price (USD)": price, "24h Change": change_24h, "Market Cap": market_cap})

        if name == "Dogecoin":  # ✅ Stop at Dogecoin
            break
    except:
        continue

driver.quit()

if data:
    df = pd.DataFrame(data)
    try:
        df = pd.concat([pd.read_csv("crypto_prices.csv"), df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv("crypto_prices.csv", index=False)
    print("✅ Done!\n")
    print(df.tail(10).to_string(index=False))  # ✅ Shows only latest 10