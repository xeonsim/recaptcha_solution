from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import urllib
import pydub
import speech_recognition as sr
import stem.process
from stem import Signal
from stem.control import Controller
from selenium.common.exceptions import NoSuchElementException

project_path = os.path.join(sys.path[0])

opt = Options()
opt.add_experimental_option("debuggerAddress", "localhost:8989")
driver = webdriver.Chrome(
    executable_path=project_path + "/chromedriver.exe",
    chrome_options=opt,
)
wait = WebDriverWait(driver, 60)


def solve_recaptcha():
    def check_exists_by_xpath(xpath):
            try:
                driver.find_element_by_xpath(xpath)
            except NoSuchElementException:
                return False
            return True
    def delay(waiting_time=5):
        driver.implicitly_wait(waiting_time)

    displayOk = check_exists_by_xpath('//*[@id="recaptcha-demo"]/div/div/iframe')
    print(displayOk)
    if displayOk:
        try:
            iframes = driver.find_elements_by_tag_name("iframe")
            driver.switch_to.frame(iframes[0])
        except:
            pass
                
        try:
            check_button = WebDriverWait(driver, 10).until(ExpectedConditions.presence_of_element_located((By.XPATH,'//*[@id="recaptcha-anchor"]/div[1]')))  
            check_button.click()
        except:
            pass

        try:
            driver.switch_to.default_content() 
            driver.switch_to.frame(iframes[-1])
        except:
            pass

        try:
            ssd=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#recaptcha-audio-button")))
            ssd.click()
            time.sleep(1)
        except:
            pass
                
        try:        # get the mp3 audio file
            delay()
            src = driver.find_element_by_id("audio-source").get_attribute("src")
            print(f"[INFO] Audio src: {src}")
                
            path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
            path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))
                
                    # download the mp3 audio file from the source
            urllib.request.urlretrieve(src, path_to_mp3)
        except:
            pass
                    

                # load downloaded mp3 audio file as .wav
        try:
            sound = pydub.AudioSegment.from_mp3(path_to_mp3)
            sound.export(path_to_wav, format="wav")
            sample_audio = sr.AudioFile(path_to_wav)
        except Exception:
            sys.exit(
                "[ERR] Please run program as administrator or download ffmpeg manually, "
                "https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/"
            )

        try: 
                # translate audio to text with google voice recognition
            delay()
            r = sr.Recognizer()
            with sample_audio as source:
                audio = r.record(source)
            key = r.recognize_google(audio)
            print(f"[INFO] Recaptcha Passcode: {key}")

                # key in results and submit
            delay()
            driver.find_element_by_id("audio-response").send_keys(key.lower())
            driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)

            driver.switch_to.default_content()     
            time.sleep(2)  
        except:
            pass
        displayOk=False