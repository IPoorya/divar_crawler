from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from unidecode import unidecode
import time, logging
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
        logging.basicConfig(level=logging.WARNING)
        max_retries = 5
        self.page_source = ''

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
        self.token = token
        self.driver.get(f"https://divar.ir/v/-/{token}")
        time.sleep(wait) # time for page content to load
        self.price_mode = self._post_kind()
        self.page_source = self.driver.page_source

    def exists(self):
        '''
            checks if a post is available or not

        '''
        try:
            if not self.page_source:
                raise Exception("First use post.get(token) then check if it exists")
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'kt-page-title__title')))
            return True
        except Exception as e:
            print(e)
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
        date = self.driver.execute_script("return document.getElementsByClassName('kt-page-title__subtitle kt-page-title__subtitle--responsive-sized');")

        if not date:
            return None
        text = date[0].text
        text = [unidecode(text.split()[0].strip()), text.split()[1].strip()]
        return text
    

    
    def data(self):
        '''
            gets the post's meterage, build, rooms, (elevator or balcony), parking, and storage status + prices

        '''
        data = []
        info = self._get_info()
        prices, extra_data= self._get_price()

        for price in prices:
            record = {}
            for item in extra_data:
                record.update(item)
            record.update(info)
            record.update(price)
            data.append(record)


        if not prices:
            # didn't have price
            return False

        return data

         


    def _is_number(self, str):
        try:
            float(str)
            return True
        except ValueError:
            return False
                
    def _get_number(self, str):
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

    def _post_kind(self):
        element = self.driver.execute_script("return document.getElementsByClassName('kt-feature-row');")
        if element:
            return True # dynamic price
        return False # static price
    
    def _get_info(self):
        element = self.driver.execute_script("return document.getElementsByClassName('kt-group-row-item');")

        data = [item.text for item in element]
        info = {}
        counter = 0
        for d in data:
            if d == "متراژ":
                 info['meterage'] = int(unidecode(data[counter+3]))
            elif d == "ساخت":
                 info["build"] = int(unidecode(data[counter+3]))
            elif d == "اتاق":
                 info["rooms"] = int(unidecode(data[counter+3]))
            elif "آسانسور" in d:
                 info["elevator"] = 1 if d == "آسانسور" else 0
            elif "پارکینگ" in d:
                 info["parking"] =  1 if d == "پارکینگ" else 0
            elif "انباری" in d:
            	 info["storage"] = 1 if d == "انباری" else 0
            elif "بالکن" in d:
                 info["balcony"] = 1 if d == "بالکن" else 0

            counter += 1

        return info
    
    def _get_price(self):
            price = []
            extra_data = []
            if self.price_mode: # price is dynamic (it's a rent post)
                element = self.driver.execute_script("return document.getElementsByClassName('kt-col-6');")
                if not element:
                    time.sleep(2)
                    element = self.driver.execute_script("return document.getElementsByClassName('kt-col-6');")
                element = [e.text for e in element]
                for i in range(4):
                    price.append(
                        self._get_number(element[i])
                        if self._is_number(unidecode(element[i].split()[0]))
                        else 0
                    )
                price = [{"price1": price[0], "price2": price[2]},
                         {"price1": price[1], "price2": price[3]}]
            
            else: # price is static (could be both rent or sell post)
                element = self.driver.execute_script("return document.getElementsByClassName('kt-unexpandable-row__value');")
                if not element:
                    time.sleep(2)
                    element = self.driver.execute_script("return document.getElementsByClassName('kt-unexpandable-row__value');")
                element = [e.text for e in element]

                for item in element:
                    # ground area comes before the prices, so if we dont have any prices yet and the item is numeric, it means it's gound area(house and villa posts)
                    # it's not price but the element has the prices class and for finding it we are reading prices so we add it to this method
                    if not price and self._is_number(item): 
                        extra_data.append({'ground_meterage': float(item)})
                    elif item != "توافقی" and 'تومان' in item:
                        price.append(
                            self._get_number(item)
                            if self._is_number(
                                unidecode("".join(item.split()[0].split("٬")))
                            )
                            else 0
                        )

                if not price:
                    return False
                
                price = [{"price1": price[0], "price2": price[1]}]

            return price, extra_data
    

    def driverQuit(self):
        '''
        Quit the WebDriver
        
        '''
        self.driver.quit()
