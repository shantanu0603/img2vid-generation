# video_generator.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import psutil
import time
import subprocess
import os

class VideoGenerator:
    def __init__(self):
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.user_data_dir = r"C:\Users\Shantanu\AppData\Local\Google\Chrome\User Data"

    def is_chrome_running(self):
        for proc in psutil.process_iter(['name']):
            if 'chrome.exe' in proc.info['name'].lower():
                return True
        return False

    def join_chrome_session(self):
        chrome_options = Options()
        chrome_options.add_argument("--remote-debugging-port=9222")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver

    def upload_image(self, driver, wait, image_path, image_xpath):
        try:
            file_input = wait.until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            file_input.send_keys(os.path.abspath(image_path))
            
            wait.until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'loading') or contains(@class, 'spinner')]"))
            )
            print("Image uploaded successfully!")
        except Exception as e:
            print(f"Upload failed with direct method. Error: {e}")
            raise

    def enter_prompt(self, driver, wait, prompt):
        prompt_locators = [
            "//*[@id='form-container']/div[2]/div[1]/div[3]/textarea",
            "//textarea[@placeholder='Upload a picture of your subject and enter your text to start creating the video. The video will focus on the main subject of your images!']",
            "//div[contains(@class, 'prompt-input')]//textarea",
            "//*[contains(@id, 'prompt-textarea')]",
            "//*[@id='radix-:rq:-content-character2video']/div[1]/div/textarea"
        ]
        
        for locator in prompt_locators:
            try:
                prompt_area = wait.until(EC.presence_of_element_located((By.XPATH, locator)))
                prompt_area.clear()
                prompt_area.send_keys(prompt)
                print(f"Prompt entered successfully using locator: {locator}")
                return
            except Exception as e:
                print(f"Failed with locator {locator}: {e}")
        
        raise Exception("Could not find prompt input area")

    def click_generate_button(self, driver, wait, timeout=30):
        generate_button_locators = [
            "//button[contains(., 'Create')]",
            "//button[.//div[contains(span, 'Create') and contains(span, 'credits')]]",
            "//button[contains(text(), 'Create')]",
            "//button[contains(., 'Create')]",
            "//button[.//span[text()='Create']]",
            "//button[contains(@class, 'generate') or contains(@class, 'create')]"
        ]
        
        for locator in generate_button_locators:
            try:
                generate_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, locator))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", generate_button)
                time.sleep(1)
                generate_button.click()
                print(f"Successfully clicked generate button using locator: {locator}")
                return True
            except TimeoutException:
                print(f"Timeout: Button not clickable with locator {locator}")
            except Exception as e:
                print(f"Error clicking button with locator {locator}: {e}")
        
        print("Failed to click generate button with all provided locators")
        return False

    def wait_for_video(self, driver, wait, max_wait_time=300, poll_interval=10):
        elapsed_time = 0
        video_url = None

        while elapsed_time < max_wait_time:
            video_url = self.get_video_link(driver, wait)
            if video_url:
                return video_url
            time.sleep(poll_interval)
            elapsed_time += poll_interval
            print(f"Waiting for video... {elapsed_time}/{max_wait_time} seconds elapsed.")
        
        return None

    def get_video_link(self, driver, wait):
        try:
            video_element = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//video[contains(@class, '') and @mediatype='video']")
                )
            )
            video_url = video_element.get_attribute("src")
            if video_url:
                print(f"Video URL extracted: {video_url}")
                return video_url
            else:
                print("Video URL not found in the 'src' attribute.")
                return None
        except TimeoutException:
            print("Timeout: Video element not found.")
            return None
        except Exception as e:
            print(f"Error retrieving video URL: {e}")
            return None

    def process_images(self, image1_path, image2_path, prompt):
        try:
            if self.is_chrome_running():
                driver = self.join_chrome_session()
            else:
                subprocess.Popen([self.chrome_path, "--remote-debugging-port=9222", f"--user-data-dir={self.user_data_dir}"])
                time.sleep(3)
                chrome_options = Options()
                chrome_options.add_argument(f"user-data-dir={self.user_data_dir}")
                chrome_options.add_argument("profile-directory=Default")
                chrome_options.add_argument("--remote-debugging-port=9222")
                chrome_options.add_argument("--disable-gpu")
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)

            wait = WebDriverWait(driver, 20)

            # Navigate to Vidu Studio
            driver.get("https://www.vidu.studio/create/character2video")
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))

            # Upload images
            image1_xpath = "//input[@type='file']"
            image2_xpath = "//input[@type='file']"

            self.upload_image(driver, wait, image1_path, image1_xpath)
            self.upload_image(driver, wait, image2_path, image2_xpath)

            # Enter Prompt
            self.enter_prompt(driver, wait, prompt)

            # Click Generate Button
            self.click_generate_button(driver, wait)

            # Wait for Video Generation and Get the Link
            video_url = self.wait_for_video(driver, wait)

            if video_url:
                return "Video generated successfully!", video_url
            else:
                return "Failed to retrieve the video URL. Please check manually.", None

        except Exception as e:
            return f"An error occurred: {str(e)}", None
        finally:
            driver.quit()