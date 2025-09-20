from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.parse
import time
import os

def setup_chrome_with_profile(profile_name="whatsapp_profile", headless=True):
    """Setup Chrome with persistent profile to maintain WhatsApp login"""
    chrome_options = Options()
    
    profile_dir = os.path.join(os.getcwd(), "chrome_profiles", profile_name)
    os.makedirs(profile_dir, exist_ok=True)
    
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    if headless:
        chrome_options.add_argument("--headless")
    
    return chrome_options

def check_login_status(driver, timeout=10):
    """Check if user is already logged into WhatsApp Web"""
    try:
        wait = WebDriverWait(driver, timeout)
        qr_code = driver.find_elements(By.CSS_SELECTOR, "[data-ref]")
        if qr_code:
            return False
        
        main_selectors = [
            "//div[@id='main']",
            "//div[contains(@class, 'two')]",
            "//div[@data-testid='chat-list']",
            "//span[@title='New chat']"
        ]
        
        for selector in main_selectors:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                return True
            except:
                continue
        
        return False
    except:
        return False

def wait_for_login(driver, max_wait=60):
    """Wait for user to scan QR code and login"""
    print("👉 Please scan the QR code to login...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if check_login_status(driver):
            print("✅ Login successful!")
            return True
        time.sleep(2)
    
    print("❌ Login timeout. Please try again.")
    return False

def send_whatsapp_message(phone, message, profile_name="whatsapp_profile"):
    """Send WhatsApp message with persistent login"""
    
    profile_dir = os.path.join(os.getcwd(), "chrome_profiles", profile_name)
    is_profile_empty = not os.path.exists(profile_dir) or not os.listdir(profile_dir)
    
    if is_profile_empty or not os.path.exists(profile_dir):
        print("🔐 No login session found. Opening browser for QR code scanning...")
        chrome_options = setup_chrome_with_profile(profile_name, headless=False)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        try:
            driver.get("https://web.whatsapp.com")
            time.sleep(3)
            
            if not wait_for_login(driver, max_wait=120):
                print("❌ Login failed")
                return False
            print("✅ Login successful! Closing browser and switching to headless mode...")
        finally:
            driver.quit()
    
    chrome_options = setup_chrome_with_profile(profile_name, headless=True)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        print(f"📱 Opening chat with {phone}...")
        chat_url = f"https://web.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"
        driver.get(chat_url)
        time.sleep(3)
        
        if not check_login_status(driver, timeout=5):
            print("🔐 Session invalid. Please run /setup-login again.")
            return False
        
        wait = WebDriverWait(driver, 30)
        print("⏳ Waiting for chat to load...")
        
        input_selectors = [
            "//div[@contenteditable='true'][@data-tab='10']",
            "//div[@contenteditable='true'][@role='textbox']",
            "//div[@contenteditable='true'][contains(@class, 'selectable-text')]",
            "//div[@title='Type a message']",
            "//div[contains(@class, 'copyable-text') and @contenteditable='true']"
        ]
        
        input_box = None
        for selector in input_selectors:
            try:
                input_box = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                print(f"✅ Found input box with selector: {selector}")
                break
            except:
                continue
        
        if not input_box:
            print("❌ Could not find input box. Trying send button approach...")
            send_button_selectors = [
                "//span[@data-icon='send']",
                "//button[contains(@class, 'send')]//span[@data-icon='send']",
                "//*[@data-icon='send']/ancestor::button",
                "//div[@role='button'][@aria-label='Send']"
            ]
            
            for selector in send_button_selectors:
                try:
                    send_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    print(f"✅ Found send button: {selector}")
                    send_button.click()
                    print("✅ Message sent via send button!")
                    time.sleep(3)
                    return True
                except:
                    continue
            
            print("❌ Could not find send button either")
            return False
        
        input_box.click()
        time.sleep(1)
        
        current_text = input_box.text or input_box.get_attribute('innerText') or ""
        print(f"📝 Current text in box: '{current_text}'")
        
        if message not in current_text:
            print("📝 Typing message...")
            input_box.clear()
            input_box.send_keys(message)
            time.sleep(1)
        
        print("📤 Sending message...")
        input_box.send_keys(Keys.ENTER)
        
        time.sleep(2)
        print("✅ Message sent successfully!")
        
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("🔍 Taking screenshot for debugging...")
        try:
            driver.save_screenshot(f"whatsapp_error.png")
            print(f"📸 Screenshot saved as 'whatsapp_error.png'")
        except:
            pass
        return False
    
    finally:
        driver.quit()

def send_whatsapp_with_retry(phone, message, max_retries=3, profile_name="whatsapp_profile"):
    """Send WhatsApp message with retry mechanism and persistent login"""
    for attempt in range(max_retries):
        print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")
        try:
            if send_whatsapp_message(phone, message, profile_name):
                return True
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            print("⏳ Waiting before retry...")
            time.sleep(5)
    
    print("❌ All attempts failed")
    return False

def setup_whatsapp_login(profile_name="whatsapp_profile"):
    """One-time setup function to login and save session"""
    print("🔧 Setting up WhatsApp Web login...")
    
    chrome_options = setup_chrome_with_profile(profile_name, headless=False)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        driver.get("https://web.whatsapp.com")
        print("👉 Please scan the QR code to complete setup...")
        
        if wait_for_login(driver, max_wait=120):
            print("✅ Setup complete! You can now send messages without logging in again.")
            time.sleep(5)
            return True
        else:
            print("❌ Setup failed. Please try again.")
            return False
            
    finally:
        driver.quit()

def clear_saved_login(profile_name="whatsapp_profile"):
    """Clear saved login data"""
    import shutil
    profile_dir = os.path.join(os.getcwd(), "chrome_profiles", profile_name)
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
        print("🗑️ Saved login data cleared!")
    else:
        print("ℹ️ No saved login data found.")