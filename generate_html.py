from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


# Start the Dash app in the background
import subprocess
app_process = subprocess.Popen(["python", "app.py"])
time.sleep(5)  # wait for server to start

# Set up headless Chrome safely for CI
options = Options()
options.headless = True
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Access the local Dash app
driver.get("http://127.0.0.1:8050")
time.sleep(3)  # wait for the page to load

# Save HTML
html = driver.page_source
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

# Cleanup
driver.quit()
app_process.terminate()
