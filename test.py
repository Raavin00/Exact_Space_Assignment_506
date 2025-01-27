import json
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_proxy_and_browser():
    # Start BrowserMob Proxy
    server = Server("./browsermob-proxy/browsermob-proxy-2.1.4/bin/browsermob-proxy") 
     # Path to browsermob-proxy
    server.start()
    proxy = server.create_proxy()

    # Configure Chrome with proxy and headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--proxy-server={proxy.proxy}")

    chrome_service = Service("/path/to/chromedriver")  
    # Path to your chromedriver
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    return server, proxy, driver

def generate_har(proxy, driver, url, output_file):
    proxy.new_har("exactspace", options={"captureContent": True})
    driver.get(url)
    driver.implicitly_wait(10)  # Wait for the page to load
    har_data = proxy.har
    with open(output_file, "w") as file:
        json.dump(har_data, file)
    print(f"HAR file saved to: {output_file}")

def analyze_har(har_file):
    with open(har_file, "r") as file:
        har_data = json.load(file)

    entries = har_data["log"]["entries"]
    total_status_count = len(entries)
    status_2xx_count = sum(1 for entry in entries if 200 <= entry["response"]["status"] < 300)
    status_4xx_count = sum(1 for entry in entries if 400 <= entry["response"]["status"] < 500)
    status_5xx_count = sum(1 for entry in entries if 500 <= entry["response"]["status"] < 600)

    print(f"Total status codes: {total_status_count}")
    print(f"Total 2XX status codes: {status_2xx_count}")
    print(f"Total 4XX status codes: {status_4xx_count}")
    print(f"Total 5XX status codes: {status_5xx_count}")

def main():
    url = "https://exactspace.co/"
    har_file = "exactspace.har"

    try:
        server, proxy, driver = setup_proxy_and_browser()
        generate_har(proxy, driver, url, har_file)
        analyze_har(har_file)
    finally:
        driver.quit()
        server.stop()

if __name__ == "__main__":
    main()
