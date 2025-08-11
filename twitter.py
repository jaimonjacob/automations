from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("X_USERNAME")
PASSWORD = os.getenv("X_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def login_and_post():
    driver = webdriver.Chrome()
    driver.get("https://twitter.com/login")

    try:
        # Wait for username field and enter username
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "text"))
        ).send_keys(USERNAME + Keys.RETURN)
        time.sleep(2)

        # Wait for password field and enter password
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password"))
        ).send_keys(PASSWORD + Keys.RETURN)
        time.sleep(5)

        # Wait for home page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/compose/tweet']"))
        )

        # Click on Tweet button or go to compose
        driver.get("https://twitter.com/compose/tweet")
        time.sleep(2)

        # Enter the tweet text
        tweet_text = "Exploring the future of AI with Gemini 2.0 Flash! #AI #Gemini"
        tweet_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Tweet text']"))
        )
        tweet_box.send_keys(tweet_text)

        # Click Tweet button
        tweet_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButton']"))
        )
        tweet_button.click()

        print("Tweet posted successfully!")

    except Exception as e:
        print("Error:", e)
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    login_and_post()