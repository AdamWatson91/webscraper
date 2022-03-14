from multiprocessing.connection import wait
from sqlite3 import ProgrammingError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itertools import groupby
import urllib.request
import time
import uuid
import os
import json
from typing import Optional, Iterable
import boto3
import tempfile
from sqlalchemy import create_engine
import pandas as pd
import re
from tqdm import tqdm
import numpy as np


class Scraper:
    """

    This class provides the main functionality required to webscrape data
    using Chrome Webdriver.

    Args:
        url (str) : The url to begin the web scarper
        options (str): The desired web driver options to the user desires
            (default is None)

    Attributes:
    driver:
        This is the webdriver object.
    """
    def __init__(self, url: str, options: Optional[str] = None) -> None:
        """See help(Scraper) for accurate signature."""
        self.url = url
        if options:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.url)
        self.client = boto3.client('s3')
        with open('/home/adamw/Documents/AWS/RDS/webscraper-1/postgress_conn.json', mode='r') as f:
            database_dict = json.load(f)
        self.engine = create_engine(f"{database_dict['DATABASE_TYPE']}+{database_dict['DBAPI']}://{database_dict['USER']}:{database_dict['PASSWORD']}@{database_dict['HOST']}:{database_dict['PORT']}/{database_dict['DATABASE']}")
        # ENHANCEMENT : The below will error if the table does not already exist. how to avoid ?
        try:
            self.df = pd.read_sql('recipe', self.engine)
            self.scraped_ids = list(self.df['recipe_id'])
            self.scraped_links = list(self.df['link'])
        except ProgrammingError:
            print('No SQL table found during scraper iniatlisation')
            pass

    @staticmethod
    def create_json(path: str, file_name: str, dict_name: str) -> None:
        """
        This function creates a json file from a dictionary.

        Args:
            path (str): The full directory path that the user wants to save the
                        file to.
            file_name (str): The desired name for the file which will be saved
                                in the path.
            dict_name (str): The dictionary to be stored as a json file.
        """
        with open(os.path.join(path, file_name), mode='w') as f:
            json.dump(dict_name, f)
        time.sleep(1)

    @staticmethod
    def get_root_path() -> str:
        """
        This function provides the root directory for the module.

        Returns:
            root_path (str): The directory for which the module is run from.
        """
        root_path = os.getcwd()
        return root_path

    @staticmethod
    def extract_continous_digit_group(iterable_element: Iterable[str]) -> str:
        """
        This functions identifies a continuous set of numbers in a string
        and returns it.

        It is common for a URL to include a unique identifier for the subject
        of the page. This function can be used to extract this by looping
        through an iterable and checking where there is a string with multiple
        digits. These digits are reutrned as a string.

        Args:
            iterable_element (Iterable[str]): The iterable string for which the
                user wants to extract a continuous digit

        Returns:
            digit_group (str): The string of continuous digits extracted from
                the iterable string.
        """
        digit_group = [int(''.join(group)) for key, group in groupby(iterable=iterable_element, key=lambda e: e.isdigit()) if key]
        return str(digit_group[0])

    def accept_cookies(self, xpath: str, iframe: Optional[str] = None) -> None:
        """
        This function will click an accept cookies button.

        Args:
            xpath (str): Xpath link for the accept cookies button which will
                be clicked once found.
            iframe (str): Xpath link for the iframe with the accept cookie
                button.
                (default is None)
        """
        time.sleep(2)
        try:
            self.driver.switch_to(iframe)
            accept_cookies_button = self.driver.find_element(By.XPATH, xpath)
            accept_cookies_button.click()
            time.sleep(2)
        except TypeError:
            accept_cookies_button = self.driver.find_element(By.XPATH, xpath)
            accept_cookies_button.click()
            time.sleep(2)
        else:
            print('No cookies button clicked with xpath provided')

    def perform_search_with_bar(self, xpath: str, text: str) -> None:
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
        time.sleep(1)  # Sleep to monitor testing
        search_bar.send_keys(Keys.ENTER)

    def scrape_element(self, xpath: str) -> str:
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

    def scrape_page_elements(self, xpath: str) -> list:
        """
        This function will find and scrape a list of elements.
        Each list element will be converted to text.

        Args:
            xpath (str): Xpath link for the element to be scraped.
        
        Returns:
            data (list): a list of string representing the text in the
                specified elements list.
        """
        data = self.driver.find_elements(By.XPATH, xpath)
        data = [i.text for i in data]
        return data

    def scrape_multiple_page_elements(self, **kwargs: str) -> dict:
        """
        This function scrapes n elements input by the user and
        stores them in a dictionary, ready for JSON.

        User can use .update() after running this to add to an
        existing dictionary.

        Args:
            kwargs (dict): The key should be the name for scraped element and
                            the value should be the xpath for the element.
        Returns:
            scraped_dict (dict): a dictionary representing the key(s)
                name specified with the a list of strings for each item in
                the specified elements list.
        """
        scraped_dict = {}
        for k, v in kwargs.items():
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, v))
                )
                v_element = self.driver.find_elements(By.XPATH, v)
                v_element = [str(i.text).replace("\n", " ") for i in v_element]
            except TimeoutException:
                print(f'{k} - No Element found')
                v_element = 'NA'
            scraped_dict[k] = v_element
        return scraped_dict

    def navigate_to(self, xpath: str, link_tag: str) -> None:
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
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
            )
        time.sleep(1)

    def scroll_infinite(self, max_scroll: int = None) -> None:
        """
        This function will scroll infinity to the specified number of scrolls.

        Args:
            max_scroll (int): The number of scrolls the user would like to
                perform.
                (default is None)
        """
        # ENHANCEMENT: Could ask user number of products per page and the number products they want to calculate the max scroll
        # ENHANCEMENT: or simply change max_scroll to number of elemnts desired.
        scroll_count = 0
        previous_height = self.driver.execute_script(
            "return document.body.scrollHeight"
            )
        while True:
            # do the scrolling
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(2)

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
                )
            if new_height == previous_height:
                break
            scroll_count += 1
            previous_height = new_height
            if scroll_count == max_scroll and max_scroll is not None:
                break

    def scrape_page_links(self, xpath: str, max_scroll: int = None) -> list:
        """
        This function will scroll infinity and scrape all of the desired 'href'
        elements using the xpath.

        Args:
            xpath (str): The x path elements to be scraped
            max_scroll (int): The number of scrolls the user would like to
                perform.
                (default is None)
        Returns:
            link (list): a list of strings representing the text for the url
                    for the specified elements list.
        """
        scroll_count = 0
        previous_height = self.driver.execute_script(
            "return document.body.scrollHeight"
            )
        while True:
            # do the scrolling
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
                )

            time.sleep(3)
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
                )
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

    @staticmethod
    def generate_uuid4() -> str:
        """
        This function will generate a random unquie identifier using the uuid4
        format.

        Returns:
            uuid_four (str): a string representing the random uuid4.
        """
        uuid_four = str(uuid.uuid4())
        return uuid_four

    def download_image(self, xpath: str, file_name: str) -> str:
        """
        This function will find the 'src' attribute for the image and download
        the image to a specified file name.

        The download will occur in the root folder for the project. The user
        can specify the directory for the file to be saved by entering the full
        root path (including desired file name) as the file_name arg.

        If the element entered is not found the function will print a message
        notifying the user and return None as the output.

        Args:
            xpath (str): The x path element to be scraped that includes the
                'src' element.
            file_name (str): The desried file_name.

        Returns:
            result (str): The string returned specifies whether the process
                 sucessfully downloaded an image.
        """
        try:
            img = self.driver.find_element(By.XPATH, xpath).get_attribute('src')
            urllib.request.urlretrieve(img, file_name)
            result = 'Image downloaded'
            return result
        except NoSuchElementException:
            print('No image was found with the element supplied')
            result = 'No image downloaded'
            return result

    def upload_image(self, xpath: str, file_name: str, bucket_name: str, directory: str) -> str:
        """
        This function will find the 'src' attribute for the image and upload
        the image with a specified file name to an S3 bucket.

        The download will occur in a temp directory to save storage. The user
        can specify the file_name to be used when uploaded. Note if a file
        exists with the same name it will be overwritten.

        If the element entered is not found the function will print a message
        notifying the user and return None as the output.

        Args:
            xpath (str): The x path element to be scraped that includes the
                'src' element.
            file_name (str): The desried file_name.
            bucket_name (str): The name of the s3 bucket the user wants to
                upload too.
            directory (str): The name of the directory to be used for storing
                the file in the s3 bucket. It should be a string of categories
                seperated by '/' and the non-alphanumeric chracters should be
                removed as best practice but this is optional.

        Returns:
            result (str): The string returned specifies whether the process
                 sucessfully downloaded an image.
        """
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            with tempfile.TemporaryDirectory() as tmpdirname:
                img = self.driver.find_element(By.XPATH, xpath).get_attribute('src')
                temp_file = os.path.join(tmpdirname, file_name)
                urllib.request.urlretrieve(img, temp_file)
                self.client.upload_file(temp_file, bucket_name, os.path.join(directory, file_name))
                result = 'Image uploaded'
            return result
        except NoSuchElementException:
            print('No image was found with the element supplied')
            result = 'No image uploaded'
            return result
        except TimeoutException:
            print('No image was found with the element supplied')
            result = 'No image uploaded'
            return result

    @staticmethod
    def create_directory(directory_name: str, directory_path: str) -> None:
        """
        This function creates a folder in the directory desired with the name
        desired.

        Args:
            directory_name (str): The name for the new directory that will be
                created.
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
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)

    def upload_directory(self, path: str, bucket_name: str) -> None:
        """
        This function uploads a local directory to a sepcified AWS s3 bucket.

        The function will identify the path and file names within the
        provided directory and write to the specified s3 bucket based on this.
        This function relies on the user configuring their IAM user with aws
        configure prior to calling the function.

        Credit to: https://www.developerfiles.com/upload-files-to-s3-with-python-keeping-the-original-folder-structure/

        Args:
            path (str): The root path for which all items within will be
                uploaded.
            bucket_name (str): The name of the bucket that the user wants to
                upload too.
        """
        session = boto3.Session()
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_name)

        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as data:
                    bucket.put_object(Key=full_path[len(path)+1:], Body=data)
    
    @staticmethod
    def create_df_from_dict(field_list: list, dictionary: dict) -> pd.DataFrame:
        """
        This function converts a specified dictionary items into a dataframe.

        The user can enter a list of dictionary keys as the field list
        they want to use as columns in the DataFrame. If dictionary
        value is a list then this method will iterate through the list
        and create a row in the DataFrame for each item in the list.
        This method will convert items to a list if they are scalar to
        enable to DataFrame to be created.

        Args:
            field_list (list): The keys from the dictionary that will be
                used as the columns.
            dictionary (dict): The dictionary that has the data to create the
                table.

        Returns:
            df (pd.DataFrame): The dataframe with columns as the keys specified
                and rows as the values from those keys. If the value was a list
                a row is created for each value in the list.
        """
        try:
            df = pd.DataFrame({key: value for key, value in dictionary.items() if key in field_list})
            return df
        except ValueError:  # If using all scalar values, you must pass an index
            df = pd.DataFrame([{key: value for key, value in dictionary.items() if key in field_list}])
            return df


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    URL = 'https://www.allrecipes.com/search/results/?search='
    bot = Scraper(URL, options)
    bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]', None)
    # bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')
    # ENHANCEMENT: Consider already scraped links in here
    # ENHANCEMENT: scroll till a specified length
    # ENHANCEMENT: add a progress bar
    links = bot.scrape_page_links(
        '//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',
        30
        )
    count = 0
    links = [x for x in links if x not in bot.scraped_links]
    for index, link in tqdm(enumerate(links[0:400])):
        print(f'\nThe link being scraped is - {link}')
        print(index)
        index_2 = index + 1
        print(f'the next link in the index is {links[index_2]}')
        # ENHANCEMENT: Download multiple images
        bot.driver.get(link)
        recipe_dict = {
            'recipe_uuid4': bot.generate_uuid4(),
            'recipe_id': bot.extract_continous_digit_group(link),
            'link': link,
            }
        scraped_page_dict = bot.scrape_multiple_page_elements(
            ingredient_list='//span[@class="ingredients-item-name elementFont__body"]',
            recipe_meta='//div[@class="recipe-meta-item"]',
            direction_steps='//span[@class="checkbox-list-text elementFont__subtitle--bold"]',
            directions_instructions='//div[@class="section-body elementFont__body--paragraphWithin elementFont__body--linkWithin"]/div[@class="paragraph"]/p',
            nutrition_summary='//div[@class="section-body"]',
            sub_categories='//span[@class="breadcrumbs__title"]'
            )
        recipe_dict.update(scraped_page_dict)
        try:
            sub_cat = os.path.join("AllRecipes", re.sub(r'\W+', '', recipe_dict['sub_categories'][2]))
        except IndexError:
            sub_cat = os.path.join("AllRecipes", re.sub(r'\W+', '', recipe_dict['sub_categories'][-1]))
        if recipe_dict['recipe_id'] not in bot.scraped_ids:
            image_id = bot.generate_uuid4()
            # EHANCEMENT: Currently image could be uploaded here but the RDS record is not created.
            # This is because the flow might fail after uploading
            bot.upload_image('//div[@class="inner-container js-inner-container image-overlay"]/img', image_id , 'watsonaicore', sub_cat)
            recipe_df_create = bot.create_df_from_dict(['recipe_uuid4', 'recipe_id', 'link'], recipe_dict)
            ingredients_df_create = bot.create_df_from_dict(['recipe_uuid4', 'ingredient_list'], recipe_dict)
            directions_df_create = bot.create_df_from_dict(['recipe_uuid4', 'direction_steps', 'directions_instructions'], recipe_dict)
            recipe_meta_df_create = bot.create_df_from_dict(['recipe_uuid4', 'recipe_meta'], recipe_dict)
            nutrition_summary_df_create = bot.create_df_from_dict(['recipe_uuid4', 'nutrition_summary'], recipe_dict)
            # recipe_df_create = pd.DataFrame([{key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'recipe_id', 'link']}])
            # ingredients_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'ingredient_list']})
            # directions_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'direction_steps', 'directions_instructions']})
            # recipe_meta_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'recipe_meta']})
            # nutrition_summary_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'nutrition_summary']})
            image_df_create = pd.DataFrame([{
                    'image_id': image_id,
                    'recipe_id': recipe_dict['recipe_uuid4'],
                    'image_link': f"https://watsonaicore.s3.amazonaws.com/{sub_cat}/{image_id}"
                    }])
                
            if count == 0:
                recipe_df = recipe_df_create
                ingredients_df = ingredients_df_create
                directions_df = directions_df_create
                recipe_meta_df = recipe_meta_df_create
                nutrition_summary_df = nutrition_summary_df_create
                image_df = image_df_create
            else:
                recipe_df = pd.concat([recipe_df, recipe_df_create])
                ingredients_df = pd.concat([ingredients_df, ingredients_df_create])
                directions_df = pd.concat([directions_df, directions_df_create])
                recipe_meta_df = pd.concat([recipe_meta_df, recipe_meta_df_create])
                nutrition_summary_df = pd.concat([nutrition_summary_df, nutrition_summary_df_create])
                image_df = pd.concat([image_df, image_df_create])
        count += 1
        
    image_df.to_sql('image', bot.engine, if_exists='append')
    recipe_df.to_sql('recipe', bot.engine, if_exists='append')
    directions_df.to_sql('directions', bot.engine, if_exists='append')
    ingredients_df.to_sql('ingredients', bot.engine, if_exists='append')
    recipe_meta_df.to_sql('recipe_meta', bot.engine, if_exists='append')
    nutrition_summary_df.to_sql('nutrition', bot.engine, if_exists='append')
