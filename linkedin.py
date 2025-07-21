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

USERNAME = os.getenv("LINK_USERNAME")
PASSWORD = os.getenv("LINK_PASSWORD")

# --- Set your search keywords here ---
SEARCH_TERMS = "Talent Management, Recruitment, Talent Aquisition"
MAX_INVITES = 37

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

# LOGIN FLOW
driver.get("https://www.linkedin.com/login")
email_el = wait.until(EC.presence_of_element_located((By.ID, "username")))
email_el.clear()
email_el.send_keys(USERNAME)
pass_el = driver.find_element(By.ID, "password")
pass_el.clear()
pass_el.send_keys(PASSWORD)
pass_el.send_keys(Keys.RETURN)

# Wait until logged in (search bar appears)
wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, "input.search-global-typeahead__input")
))
print("✅ Logged in successfully")

# --- Build the search URL dynamically ---
encoded_terms = urllib.parse.quote(SEARCH_TERMS)
search_url = (
    f"https://www.linkedin.com/search/results/PEOPLE/"
    f"?keywords={encoded_terms}&origin=SWITCH_SEARCH_VERTICAL"
)
driver.get(search_url)

# Loop through search results, visit each profile, and connect from the profile page

sent_count = 0

while sent_count < MAX_INVITES:
    try:
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[data-chameleon-result-urn]")
        ))
    except TimeoutException:
        print("⚠️ No search results found on this page.")
        break  # If no results, break the loop immediately

    result_items = driver.find_elements(By.CSS_SELECTOR, "div[data-chameleon-result-urn]")
    processed_any = False  # Track if any profile was processed on this page

    for item in result_items:
        if sent_count >= MAX_INVITES:
            break
        try:
            # Skip if "Message" button is present in the search result (already connected or request sent)
            try:
                message_btn = item.find_element(
                    By.XPATH, ".//button[.//span[normalize-space()='Message']]"
                )
                if message_btn and message_btn.is_displayed():
                    print("🔄 Skipping: Already connected or request sent.")
                    continue
            except NoSuchElementException:
                pass  # No Message button, proceed

            # Find the profile link ("/in/" is always in LinkedIn profile URLs)
            profile_link = item.find_element(By.XPATH, ".//a[contains(@href, '/in/')]").get_attribute("href")
            if not profile_link:
                continue

            processed_any = True  # At least one profile processed on this page

            # Open profile in new tab
            driver.execute_script("window.open(arguments[0]);", profile_link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)  # Wait for profile to load

            try:
                # Wait for the main profile area to load (parent div you shared)
                main_profile = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5.pb5")))
                time.sleep(1.5)  # Wait for profile content to fully render

                # 1. Try to find the Connect button only inside the main profile section (parent div)
                try:
                    profile_connect_btn = main_profile.find_element(
                        By.XPATH, ".//button[.//span[contains(@class, 'artdeco-button__text') and normalize-space()='Connect']]"
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", profile_connect_btn)
                    time.sleep(0.7)
                    try:
                        profile_connect_btn.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", profile_connect_btn)
                    time.sleep(1.2)
                except Exception:
                    # 2. If not found, try the More menu for Connect using a div and aria-label combination
                    try:
                        more_btn = main_profile.find_element(
                            By.XPATH, ".//button[.//span[normalize-space()='More']]"
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_btn)
                        time.sleep(0.7)
                        try:
                            more_btn.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", more_btn)
                        time.sleep(1.5)
                        # Find all dropdowns with the class 'artdeco-dropdown__content'
                        dropdown_menus = driver.find_elements(By.XPATH, "//div[contains(@class, 'artdeco-dropdown__content')]")
                        connect_clicked = False
                        for dropdown_menu in dropdown_menus:
                            items = dropdown_menu.find_elements(By.XPATH, ".//div[@role='button']")
                            for item in items:
                                if item.is_displayed():
                                    text = item.text.strip()
                                    aria_label = item.get_attribute("aria-label") or ""
                                    if text == "Connect" and "Invite" in aria_label and "to connect" in aria_label:
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                                        time.sleep(0.5)
                                        try:
                                            item.click()
                                        except Exception:
                                            driver.execute_script("arguments[0].click();", item)
                                        connect_clicked = True
                                        print("Clicked the correct 'Connect' button in dropdown.")
                                        break
                            if connect_clicked:
                                break
                        if not connect_clicked:
                            print("❌ Could not find a visible 'Connect' button in any dropdown after clicking More.")
                            raise Exception("Connect not found in More menu")
                        time.sleep(1.2)
                    except Exception as e:
                        print("⚠️  Could not find Connect button in More menu:", e)
                        raise e  # Will be caught by the outer try/except

                # 3. Handle the "Send without a note" popup
                try:
                    send_wo_note = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//button[normalize-space()='Send without a note']"
                    )))
                    time.sleep(0.7)
                    send_wo_note.click()
                    sent_count += 1
                    print(f"→ Invitation #{sent_count} sent (from profile page)")
                    time.sleep(1.2)
                except Exception as e:
                    print("⚠️  Could not click 'Send without a note':", e)
            except Exception as e:
                print("⚠️  Could not send invite from profile page:", e)
            finally:
                # Close profile tab and switch back
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

        except Exception as e:
            print("⚠️  Error processing result:", e)
            continue

    if sent_count >= MAX_INVITES:
        break

    # Always try to go to the next page if there were results, even if none were processed
    try:
        # Scroll to the bottom of the page to ensure the Next button is visible
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        next_btn = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.artdeco-pagination__button--next"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
        next_btn.click()
        print("→ Next page…")
        time.sleep(2)
    except TimeoutException:
        print("🔚 No more pages. Finishing up.")
        break

print(f"✅ Done, sent {sent_count} connection request(s).")