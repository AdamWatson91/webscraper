from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import random
import uuid
# research the below options and more and decide whther to implement
# options = webdriver.ChromeOptions()
# options.add_argument('start-maximized')
# options.add_argument('disable-infobars')
# options.add_argument('--disable-extensions')
# print('this will always run')
# if __name__ == "__main__":
class Scraper:
    def __init__(self, url, options=None):
        self.url = url
        if options:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)
        self.accept_cookies
        self.perform_search_with_bar
        self.scrape_element
        self.scrape_page_elements
        self.navigate_to
        self.scroll_page
        self.scroll_infinite
        self.scrape_page_links
        self.login

    def accept_cookies(self, xpath, iframe=None):
        time.sleep(2)
        try:
            self.driver.switch_to(iframe)
            accept_cookies_button = self.driver.find_element(By.XPATH, xpath)
            accept_cookies_button.click()
            time.sleep(2)
        except:
            accept_cookies_button = self.driver.find_element(By.XPATH, xpath)
            accept_cookies_button.click()
            time.sleep(2)
        # except:
        #     print('No cookies button clicked with with xpath provided')
    
    def perform_search_with_bar(self, xpath, text):
        search_bar = self.driver.find_element(By.XPATH, xpath)
        search_bar.clear()
        search_bar.send_keys(text)
        time.sleep(2) # Sleep for to monitor testing

    # def perform_search_with_link(self, xpath, text):
    #     search_bar = self.find_element(By.XPATH, xpath)
    #     search_bar = search_bar.send_keys()
    def scrape_element(self, xpath):
        data = self.driver.find_element(By.XPATH, xpath).text
        return data

    def scrape_page_elements(self, xpath):
        data = self.driver.find_elements(By.XPATH, xpath)
        data = [i.text for i in data]
        return data

    def navigate_to(self, xpath, link_tag):
        link = self.driver.find_element(By.XPATH, xpath)
        link = link.get_attribute(link_tag)
        self.driver.get(link)
        time.sleep(3)
    
    

    
    def scroll_page(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    def scroll_infinite(self,max_scroll=None):
        #ENHANCEMENT: Could ask user number of products per page and the number products they want to calculate the max scroll
        scroll_count = 0
        previous_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # do the scrolling
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(3)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == previous_height:
                break
            scroll_count += 1
            previous_height = new_height
            if scroll_count == max_scroll and max_scroll is not None:
                break
            
            

    def scrape_page_links(self, xpath, max_scroll=None):
        scroll_count = 0
        previous_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # do the scrolling
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == previous_height:
                links = self.driver.find_elements(By.XPATH, xpath)
                break
            scroll_count += 1
            previous_height = new_height
            if scroll_count == max_scroll and max_scroll is not None:
                links = self.driver.find_elements(By.XPATH, xpath)
                break
        link = [links.get_attribute('href') for links in links]
        return link


    def login(self, username, password, user_xpath, pass_xpath, button_xpath):
            user_entry = self.driver.find_element(By.XPATH, user_xpath)
            pass_entry = self.driver.find_element(By.XPATH, pass_xpath)
            user_entry.send_keys(username)
            pass_entry.send_keys(password)
            sign_in_button = self.driver.find_element(By.XPATH, button_xpath)
            sign_in_button.click()

    def generate_uid(self):
        seed = random.getrandbits(32)
        while True:
            yield seed
            self.uid = seed
            seed += 1
    
    def generate_uuid4(self):
        self.uuid_foir = uuid.uuid4()
    
    def download_image(self, xpath):
        img = self.driver.find_elements(By.XPATH, xpath).text
        # img = [i.text for i in data]
        return img


if __name__ == "__main__":
    URL = 'https://www.allrecipes.com/search/results/?search='
    bot  = Scraper(URL)
    bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]',None)
    bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')
    ingredient_list = bot.scrape_page_elements('//span[@class="ingredients-item-name elementFont__body"]')
    recipe_meta = bot.scrape_page_elements('//div[@class="recipe-meta-item"]')
    print(ingredient_list)
    print(recipe_meta)
    main_image = bot.download_image('//div[@class="component lazy-image lazy-image-udf lead-media ugc-photos-link aspect_3x2 rendered image-loaded"]')
    print(main_image)
    # #bot.perform_search_with_bar('//*[@id="primary-search"]', 'some text')
    # bot.scroll_page()
    # bot.scroll_infinite()
    # links = bot.scrape_page_links('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 2)
    # print(links)
    # path for the main image //div[@class='component lazy-image lazy-image-udf lead-media ugc-photos-link aspect_3x2 rendered image-loaded']

