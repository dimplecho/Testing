from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from googletrans import Translator 
from collections import Counter  

# BrowserStack credentials
BROWSERSTACK_USERNAME = 'dimplechoudhary_MULyCR'
BROWSERSTACK_ACCESS_KEY = 'ozEMKk1t1pSxwbvNoZag'

# Function to translate text
def translate_text(text, target_language='en'):
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest=target_language).text
        return translated_text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def get_browserstack_driver(browser, platform, version):
    desired_cap = {
        'browser': browser,
        'browser_version': version,
        'os': platform,
        'os_version': 'latest', 
        'name': 'Selenium WebDriver Test',
        'build': '1.0',
        'browserstack.local': 'false',
    }


    if browser == 'Chrome':
        options = webdriver.ChromeOptions()
    elif browser == 'Firefox':
        options = webdriver.FirefoxOptions()  
    elif browser == 'Edge':
        options = webdriver.EdgeOptions()  
    elif browser == 'Safari':
        options = webdriver.SafariOptions()  
    else:
        raise ValueError("Unsupported browser")

    driver = webdriver.Remote(
        command_executor=f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub",
        options=options  
    )

    driver.capabilities.update(desired_cap)
    return driver

browsers = [
    {'browser': 'Chrome', 'platform': 'Windows', 'version': 'latest'},
    {'browser': 'Firefox', 'platform': 'Windows', 'version': 'latest'},
    {'browser': 'Safari', 'platform': 'macOS', 'version': 'latest'},
    {'browser': 'Edge', 'platform': 'Windows', 'version': 'latest'},
    {'browser': 'Chrome', 'platform': 'Android', 'version': 'latest'},
    {'browser': 'Safari', 'platform': 'iOS', 'version': 'latest'}
]

for config in browsers:
    try:
        print(f"Testing on Browser: {config['browser']} on {config['platform']}")       
        driver = get_browserstack_driver(config['browser'], config['platform'], config['version'])

        # Open the page on BrowserStack
        driver.get("https://elpais.com/")

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Navigate to the "Opinión" section
        try:
            opinion_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Opinión"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", opinion_link) 
            driver.execute_script("arguments[0].click();", opinion_link)  
            time.sleep(5)  
        except Exception as e:
            print(f"Error navigating to Opinión section: {e}")
            driver.quit()
            continue

        try:
            articles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
            )[:5]
        except Exception as e:
            print(f"Error locating articles: {e}")
            driver.quit()
            continue

        article_data = []
        translated_titles = [] 

        for idx, article in enumerate(articles):
            try:
            
                title = article.find_element(By.TAG_NAME, "h2").text
            except Exception as e:
                print(f"Title not found for article {idx + 1}: {e}")
                title = "Title not available"

            translated_title = translate_text(title)
            translated_titles.append(translated_title)  

            try:
                content = article.find_element(By.CLASS_NAME, "c_d").text  
            except Exception as e:
                print(f"Content not found for article {idx + 1}: {e}")
                content = "Content not available"

            try:
                # Extract and save the image
                image_url = article.find_element(By.TAG_NAME, "img").get_attribute("src")
                response = requests.get(image_url, stream=True)
                image_path = f"article_{idx + 1}.jpg"
                with open(image_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Image saved as {image_path}")
            except Exception as e:
                print(f"No image found for article {idx + 1}: {e}")
                image_url = None

            article_data.append({"original_title": title, "translated_title": translated_title, "content": content, "image_url": image_url})

        # Print scraped and translated data
        for idx, article in enumerate(article_data, 1):
            print(f"Article {idx}")
            print(f"Original Title: {article['original_title']}")
            print(f"Translated Title: {article['translated_title']}")
            print(f"Content: {article['content']}")
            print(f"Image URL: {article['image_url']}")
            print("-" * 40)

        # Analyze the translated titles for repeated words
        all_translated_text = " ".join(translated_titles).lower() 
        words = all_translated_text.split() 
        word_counts = Counter(words)  

        print("\nWord Counts in Translated Titles:")
        for word, count in word_counts.items():
            print(f"Word: '{word}', Count: {count}")

        repeated_words = {word: count for word, count in word_counts.items() if count > 2}

        print("\nRepeated Words in Translated Titles (appearing more than twice):")
        for word, count in repeated_words.items():
            print(f"Word: '{word}', Count: {count}")

        driver.quit()

    except Exception as e:
        print(f"Error during BrowserStack testing: {e}")
