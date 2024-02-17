from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from unidecode import unidecode
import time, os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class Post:
    def __init__(self) -> None:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--log-level=3")
        max_retries = 5

        for _ in range(max_retries):
            try:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                break  
            except Exception as e:
                print(f"Error initializing driver: {e}")
                print("Retrying...")

    def get(self, token, wait=0):
        '''
            gets the post page

        '''
        self.driver.get(f"https://divar.ir/v/-/{token}")
        page_source = self.driver.page_source
        self.soup = BeautifulSoup(page_source, "html.parser")
        time.sleep(wait) # time for page content to load

    def exists(self, token):
        '''
            checks if a post is still available or not

        '''
        if not self.soup:
            self.getPost(token)
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'kt-page-title__title')))
            return True
        except Exception as e:
            return False
        

    def location(self):
        '''
            gets the post's location

        '''
        location = self.driver.execute_script("return document.getElementsByClassName('kt-page-title__subtitle');")
        location = location[0].text.split("،")
        location = (
            [location[0].split("در")[-1].strip(), location[1].strip()]
            if len(location) == 2
            else [location[0].split("در")[-1].strip(), ""]
        )

        return location


    def date(self):
        '''
            gets the post's date

        '''
        date = self.soup.find_all(
            "div",
            class_="kt-page-title__subtitle kt-page-title__subtitle--responsive-sized",
        )
        if not date:
            return None
        text = date[0].text
        text = text.split()[0].strip()
        return unidecode(text)
    
    



def is_number(str):
            try:
                float(str)
                return True
            except ValueError:
                return False
            
def get_number(str):
            text = str.split()
            if text[1] == "میلیاردودیعه" or text[1] == "میلیارداجاره":
                num = float(text[0]) * 1000
            elif text[1] == "میلیونودیعه" or text[1] == "میلیوناجاره":
                num = float(text[0])
            elif text[1] == "هزاراجاره" or text[1] == "هزارودیعه":
                num = float(text[0]) / 1000
            elif text[1] == "تومان":
                num = int(unidecode("".join(text[0].split("٬")))) / 1000000
            return num



post = Post()
post.get('QZQDfJqG', 2)
print(post.rent_data())