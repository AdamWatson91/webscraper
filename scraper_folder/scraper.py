from multiprocessing.connection import wait
from sqlite3 import ProgrammingError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
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
import sqlalchemy
from sqlalchemy import column, create_engine
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument("no-sandbox")
# options.add_argument("--disable-dev-shm-usage")

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
        try:
            self.df = pd.read_sql('recipe', self.engine)
            self.scraped_ids = list(self.df['recipe_id'])
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
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, v))
                )
                v_element = self.driver.find_elements(By.XPATH, v)
                v_element = [str(i.text).replace("\n", " ") for i in v_element]
            except NoSuchElementException:
                print('No Element found')
                v_element = 'N/A'
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
            result (str): The string returned specifies whther the process
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

    def upload_image(self, xpath: str, file_name: str) -> str:
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

        Returns:
            result (str): The string returned specifies whther the process
                 sucessfully downloaded an image.
        """
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                img = self.driver.find_element(By.XPATH, xpath).get_attribute('src')
                urllib.request.urlretrieve(img, tmpdirname + file_name)
                # ENHANCEMENT : bucket name could be intialised instead of reference within this method
                self.client.upload_file(tmpdirname + file_name, 'watsonaicore', file_name)
                result = 'Image uploaded'
            return result
        except NoSuchElementException:
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

    def upload_directory(self, path: str, bucketname: str) -> None:
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
            bucketname (str): The name of the bucket that the user wants to
                upload too.
        """
        session = boto3.Session()
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucketname)

        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as data:
                    bucket.put_object(Key=full_path[len(path)+1:], Body=data)

    @staticmethod
    def dict_to_df(dict: dict) -> pd.DataFrame:
        """
        This function converts a dictionary to a pandas DataFrame.

        Args:
            dict (dict): The dictionary that the user want's to convert to
                a DataFrame.
        Returns:
            df (pd.DataFrame): The pandas DataFrame that is have colunms
                with the dict keys and rows with the dict values
        """
        dict_items = dict.items()
        data_list = list(dict_items)
        df = pd.DataFrame(data_list)
        return df


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    URL = 'https://www.allrecipes.com/search/results/?search='
    bot = Scraper(URL, options)
    print(bot.scraped_ids)
    bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]', None)
    # bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')

    links = bot.scrape_page_links(
        '//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',
        1
        )
    # bot.create_directory('raw_data', bot.get_root_path())

    count = 0
    for link in links[0:5]:
        print(count) # Acting as loading screen for now
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
            nutrition_summary='//div[@class="section-body"]'
            )
        recipe_dict.update(scraped_page_dict)
        if recipe_dict['recipe_id'] not in bot.scraped_ids:
            image_id = bot.generate_uuid4()
            bot.upload_image('//div[@class="inner-container js-inner-container image-overlay"]/img', image_id)
            recipe_df_create = pd.DataFrame([{key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'recipe_id', 'link']}])
            ingredients_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'ingredient_list']})
            directions_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'direction_steps', 'directions_instructions']})
            recipe_meta_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'recipe_meta']})
            nutrition_summary_df_create = pd.DataFrame({key: value for key, value in recipe_dict.items() if key in ['recipe_uuid4', 'nutrition_summary']})
            image_df_create = pd.DataFrame([{'image_id': image_id, 'recipe_id': recipe_dict['recipe_uuid4'], 'image_link': f"https://watsonaicore.s3.amazonaws.com/{image_id}"}])
                
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
        # raw_data_path = os.path.join(bot.get_root_path(), 'raw_data')
        # bot.create_directory(recipe_dict['recipe_id'][0], raw_data_path)
        # recipe_path = os.path.join(raw_data_path, recipe_dict['recipe_id'][0])
        # bot.create_json(recipe_path, 'data.json', recipe_dict)
        # bot.create_directory('images', recipe_path)
        # images_path = os.path.join(recipe_path, 'images')
        # bot.upload_image('//div[@class="inner-container js-inner-container image-overlay"]/img', recipe_dict['recipe_uuid4'][0])
        
    #     bot.download_image(
    #         '//div[@class="inner-container js-inner-container image-overlay"]/img',
    #         os.path.join(images_path, str(0))
    #         )
    # bot.upload_directory(raw_data_path, 'watsonaicore')

    print(image_df)
    print(recipe_df)
    print(ingredients_df)
    print(directions_df)
    print(recipe_meta_df)
    print(nutrition_summary_df)
    image_df.to_sql('image', bot.engine, if_exists='append')
    recipe_df.to_sql('recipe', bot.engine, if_exists='append')
    directions_df.to_sql('directions', bot.engine, if_exists='append')
    ingredients_df.to_sql('ingredients', bot.engine, if_exists='append')
    recipe_meta_df.to_sql('recipe_meta', bot.engine, if_exists='append')
    nutrition_summary_df.to_sql('nutrition', bot.engine, if_exists='append')
