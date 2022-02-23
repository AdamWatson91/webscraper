from logging import root
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from itertools import groupby
from urllib.parse import urlparse, parse_qs
import urllib.request
import requests
import time
import random
import uuid
import os
import json
from pathlib import Path

# research the below options and more and decide whther to implement
# options = webdriver.ChromeOptions()
# options.add_argument('start-maximized')
# options.add_argument('disable-infobars')
# options.add_argument('--disable-extensions')

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
    
    def scrape_multiple_page_elements_v2(self, **kwargs):
        scraped_dict = {}
        for k, v in kwargs.items():
            try:
                v_element = self.driver.find_elements(By.XPATH, v)
                v_element = [i.text for i in v_element]
            except NoSuchElementException:
                print('No Element found')
                v_element = 'N/A'
            scraped_dict[k] = v_element
        return scraped_dict

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
        parsed = urlparse(self.url)
        query = parse_qs(parsed.query)
        [page] = query['page']
    
    def generate_uuid4(self):
        self.uuid_four = uuid.uuid4()
    
    def download_image(self, xpath, file_name):
        img = self.driver.find_element(By.XPATH, xpath)
        img = img.get_attribute('src')
        urllib.request.urlretrieve(img,file_name)
    
    def create_directory(self,directory_name, directory_path ):
        # identify the root of the path
        self.directory_name = directory_name
        self.directory_path = directory_path
        self.path = os.path.join(self.directory_path, self.directory_name)
        # make the directory in the root of the project
        try:
            os.makedirs(self.path, exist_ok=True)
        except OSError:
            print ("Creation of the directory %s failed" % self.path)
        else:
            print ("Successfully created the directory %s " % self.path)



if __name__ == "__main__":
    URL = 'https://www.allrecipes.com/search/results/?search='
    bot  = Scraper(URL)
    bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]',None)
    #bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')

    links = bot.scrape_page_links('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',1)
    root_path = os.getcwd()
    bot.create_directory('raw_data', root_path)

    for link in links:
        # ENHANCEMENT: Download multiple images
        # ENHANCEMENT: Improve the path create logic, the code is fairly unreadable right now. Could create variables
        bot.driver.get(link)
        time.sleep(2)
        recipe_id = [int(''.join(group)) for key, group in groupby(iterable=link, key=lambda e: e.isdigit()) if key]
        uuid4 = bot.generate_uuid4
        recipe_dict = {
                'recipe_id': [uuid4],
                'recipe_id': [recipe_id],
                'link': [link],    
    #             'ingredient_list': [],
    #             'recipe_meta': []
                 }
        scraped_page_dict = bot.scrape_multiple_page_elements_v2(
            ingredient_list='//span[@class="ingredients-item-name elementFont__body"]', 
            recipe_meta='//div[@class="recipe-meta-item"]'
            )
        recipe_dict.update(scraped_page_dict)
        raw_data_path = os.path.join(root_path,'raw_data')
        bot.create_directory(str(recipe_id), raw_data_path)
        recipe_path = os.path.join(raw_data_path, str(recipe_id))
        with open(os.path.join(recipe_path,'data.json'), mode='w') as f:
            json.dump(recipe_dict, f)
        time.sleep(1)
        bot.create_directory('images',recipe_path)
        images_path = os.path.join(recipe_path,'images')
        bot.download_image('//div[@class="inner-container js-inner-container image-overlay"]/img', os.path.join(images_path, str(0)))

        # unit testing ideas:
        # 1. Check that the uuid4 does not duplicate
        # 2. Check it gets the images for each, could probaly att wait for element to my functions for safety
        # 3. Add extra element in does it still work
        # 4. Change website, does it still work
        # 5. If there is a duplicate id will it error
        # 6. Does the data scraped match the expected values (foudn it doesn't seem to line 1/4 or brackets like (12 Ounce))
