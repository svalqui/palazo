from playwright.sync_api import sync_playwright
import os
import time

def click_bottom_dl(my_path, my_url, my_text):
    print(my_path)
    print(my_url)
    print(my_text)
  
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(my_url)
        with page.expect_download() as download_info:
            page.click("text=" + my_text )

        download = download_info.value
        path = download.path()

        save_path = os.path.join(my_path, "data.csv")
        download.save_as(save_path)

        print("Saved to:", save_path)

        context.close()
        browser.close()
