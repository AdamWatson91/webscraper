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
from typing import Optional, Iterable


# research the below options and more and decide whther to implement
# options = webdriver.ChromeOptions()
# options.add_argument('start-maximized')
# options.add_argument('disable-infobars')
# options.add_argument('--disable-extensions')

# REFACTORING ENHANCEMENTS:
# 1. Review the functions and note where functions do the same thing and package this into a function and call it. E.g. i have many find_elements throughout
# 2. Check whether i have static methods here


class Scraper:
    """
    This class provides the main functionality required to webscrape data using Chrome Webdriver.

    Args:
        url (str) : The url to begin the web scarper
        options (str): The desired web driver options to the user desires
            (default is None)
    
    Attributes:
    driver:
        This is the webdriver object.
    """
    def __init__(self, url : str, options : Optional[str] = None) -> None:
        """
        See help(Scraper) for accurate signature.
        """
        self.url = url
        if options:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)
    
    def create_json(self, path : str, file_name : str) -> None:
        """
        This function creates a json file from a dictionary.

        Args:
            path (str): The full directory path that the user wants to save the
                        file to.
            file_name (str): The desired name for the file which will be saved 
                                in the path.
        """
        with open(os.path.join(path, file_name), mode='w') as f:
            json.dump(recipe_dict, f)
        time.sleep(1)

    def get_root_path(self) -> str:
        """
        This function provides the root directory for the module.

        Returns:
            root_path (str): The directory for which the module is run from.
        """
        root_path = os.getcwd()
        return root_path
    
    def extract_continous_digit_group(self, iterable_element : Iterable[str]) -> str:
        """
        This functions identifies a continuous set of numbers in a string 
        and returns it.

        It is common for a URL to include a unique identifier for the subject
        of the page. This function can be used to extract this by looping through 
        an iterable and checkign where there is a string with multiple digits.
        These digits are reutrned as a string.

        Args:
            iterable_element (Iterable[str]): The iterable string for which the user wants to extract a 
                                                continuous digit

        Returns:
            digit_group (str): The string of continuous digits extracted from the iterable string.
        """
        digit_group = [int(''.join(group)) for key, group in groupby(iterable=iterable_element, key=lambda e: e.isdigit()) if key]
        return str(digit_group)

    def accept_cookies(self, xpath : str, iframe : Optional[str] = None) -> None:
        """
        This function will click an accept cookies button.

        Args:
            xpath (str): Xpath link for the accept cookies button which will be clicked once found.
            iframe (str): Xpath link for the iframe with the accept cookie button.
                (default is None)
        """
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
        else:
            print('No cookies button clicked with xpath provided')
    
    def perform_search_with_bar(self, xpath : str, text : str) -> None:
        """
        This function will type and search for the inputted text 
        using the websites search bar by pressing Enter.

        Args:
            xpath (str): Xpath link for the search bar.
            text (str): The text that will be searched for.
        """
        search_bar = self.driver.find_element(By.XPATH, xpath)
        search_bar.clear()
        search_bar.send_keys(text)
        time.sleep(1) # Sleep to monitor testing
        search_bar.send_keys(Keys.ENTER)

    def scrape_element(self, xpath : str) -> str:
        """
        This function will find and scrape and convert to text
        a single element.

        Args:
            xpath (str): Xpath link for the element to be scraped.
        Returns:
            data (str): a string representing the text in the specified element
        """
        data = self.driver.find_element(By.XPATH, xpath).text
        return data

    def scrape_page_elements(self, xpath : str) -> str:
        """
        This function will find and scrape a list of elements. 
        Each list element will be converted to text.

        Args:
            xpath (str): Xpath link for the element to be scraped.
                Returns:
            data (list): a list of string representing the text in the specified elements list.
        """
        data = self.driver.find_elements(By.XPATH, xpath)
        data = [i.text for i in data]
        return data
    
    def scrape_multiple_page_elements(self, **kwargs : str) -> dict:
        """
        This function scrapes n elements input by the user and
        stores them in a dictionary, ready for JSON.

        User can use .update() after running this to add to an 
        existing dictionary.

        Args:
            kwargs (dict): The key should be the name for scraped element and 
                            the value should be the xpath for the element.
        Returns:
            scraped_dict (dict): a dictionary representing the key(s) name specified with the a list
                    of strings for each item in the the specified elements list.
        """
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

    def navigate_to(self, xpath : str, link_tag : str) -> None:
        """
        This function finds and clicks a link based on an xpath.

        Args:
            xpath (str): Xpath link for the link to be clicked.
            link_tag (str): The attribute with the hyperlink, usuall 'href'.
        """
        link = self.driver.find_element(By.XPATH, xpath)
        link = link.get_attribute(link_tag)
        self.driver.get(link)
        time.sleep(1)
    
    def scroll_page(self) -> None:
        """
        This function scrolls to bottom of the page once.

        If your webpage is an infinite scroll see function scroll_infinite().
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    def scroll_infinite(self, max_scroll : int = None) -> None:
        """
        This function will scroll infinity to the specified number of scrolls.

        Args:
            max_scroll (int): The number of scrolls the user would like to perform.
                (default is None)
        """
        # ENHANCEMENT: Could ask user number of products per page and the number products they want to calculate the max scroll
        # ENHANCEMENT: or simply change max_scroll to number of elemnts desired.
        scroll_count = 0
        previous_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # do the scrolling
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(2)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == previous_height:
                break
            scroll_count += 1
            previous_height = new_height
            if scroll_count == max_scroll and max_scroll is not None:
                break

    def scrape_page_links(self, xpath : str, max_scroll : int = None) -> list:
        """
        This function will scroll infinity and scrape all of the desired 'href' 
        elements using the xpath.

        Args:
            xpath (str): The x path elements to be scraped
            max_scroll (int): The number of scrolls the user would like to perform.
                (default is None)
        Returns:
            link (list): a list of strings representing the text for the url for the specified elements
                    list.
        """
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

    # def login(self, username, password, user_xpath, pass_xpath, button_xpath):
    #         user_entry = self.driver.find_element(By.XPATH, user_xpath)
    #         pass_entry = self.driver.find_element(By.XPATH, pass_xpath)
    #         user_entry.send_keys(username)
    #         pass_entry.send_keys(password)
    #         sign_in_button = self.driver.find_element(By.XPATH, button_xpath)
    #         sign_in_button.click()
    
    def generate_uuid4(self) -> str:
        """
        This function will generate a random unquie identifier using the uuid4 format.

        Returns:
            uuid_four (str): a string representing the random uuid4.
        """
        uuid_four = str(uuid.uuid4())
        return uuid_four

    def download_image(self, xpath : str, file_name : str) -> None:
        """
        This function will find the 'src' attribute for the image and download
        the image to a speified file name.

        The download will occur in the root folder for the project. The user can speficy 
        the directory for the file to be saved by entering the full root path 
        (including desried file name) as the file_name arg. 

        Args:
            xpath (str): The x path element to be scraped that includes the 'src' element.
            file_name (str): The desried file_name.
        """
        img = self.driver.find_element(By.XPATH, xpath).get_attribute('src')
        urllib.request.urlretrieve(img, file_name)
    
    def create_directory(self, directory_name : str, directory_path : str) -> None:
        """
        This function create a folder in the directory desired with the name desired.

        Args:
            directory_name (str): The name for the new directory that will be created.
            directory_path (str): The path to create the new directory.
        """
        # identify the root of the path
        directory_name = directory_name
        directory_path = directory_path
        path = os.path.join(directory_path, directory_name)
        # make the directory in the root of the project
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s " % path)

if __name__ == "__main__":
    URL = 'https://www.allrecipes.com/search/results/?search='
    bot = Scraper(URL)
    bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]',None)
    #bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')
    links = bot.scrape_page_links('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',1)
    bot.create_directory('raw_data', bot.get_root_path())

    for link in links:
        # ENHANCEMENT: Download multiple images
        bot.driver.get(link)
        time.sleep(2)
        # recipe_id = [int(''.join(group)) for key, group in groupby(iterable=link, key=lambda e: e.isdigit()) if key]
        recipe_dict = {
            'recipe_uuid4': [bot.generate_uuid4()],
            'recipe_id': [bot.extract_continous_digit_group(link)],
            'link': [link],    
            }
        scraped_page_dict = bot.scrape_multiple_page_elements(
            ingredient_list='//span[@class="ingredients-item-name elementFont__body"]', 
            recipe_meta='//div[@class="recipe-meta-item"]',
            direction_steps='//ul[@class="instructions-section"]/li[@class="subcontainer instructions-section-item"][*]/label[@class="checkbox-list"]',
            directions_instructions='//div[@class="section-body elementFont__body--paragraphWithin elementFont__body--linkWithin"]/div[@class="paragraph"]/p',
            nutrition_summary= '//div[@class="section-body"]'
            )
        recipe_dict.update(scraped_page_dict)
        raw_data_path = os.path.join(bot.get_root_path(),'raw_data')
        bot.create_directory(recipe_dict['recipe_id'][0], raw_data_path)
        recipe_path = os.path.join(raw_data_path, recipe_dict['recipe_id'][0])
        bot.create_json(recipe_path,'data.json')
        bot.create_directory('images',recipe_path)
        images_path = os.path.join(recipe_path,'images')
        bot.download_image('//div[@class="inner-container js-inner-container image-overlay"]/img', os.path.join(images_path, str(0)))


