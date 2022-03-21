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
        # self.key_id = input('Enter your AWS key id: ')
        # self.secret_key = input('Enter your AWS secret key: ')
        # self.bucket_name = input('Enter your s3 bucket name: ')
        # self.region = input('Enter your AWS region: ')
        self.client = boto3.client(
            's3'
            # aws_access_key_id=self.key_id
            # aws_secret_access_key=self.secret_key
            # region_name=self.region
        )
        with open(os.path.join(os.getcwd(),'postgres_conn.json'), mode='r') as f:
            database_dict = json.load(f)
        self.RDS_pass = input('Enter the password to the RDS postgress DB:')
        self.engine = create_engine(f"{database_dict['DATABASE_TYPE']}+{database_dict['DBAPI']}://{database_dict['USER']}:{self.RDS_pass}@{database_dict['HOST']}:{database_dict['PORT']}/{database_dict['DATABASE']}")
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
            WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
            )
            # self.driver.switch_to(iframe)
            accept_cookies_button = self.driver.find_element(By.XPATH, xpath)
            accept_cookies_button.click()
            time.sleep(2)
        except TypeError:
            WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
            )
            accept_cookies_button = self.driver.find_element(By.XPATH, xpath)
            accept_cookies_button.click()
            time.sleep(2)
        except TimeoutException:
            print('No cookies button clicked with xpath provided')
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
 
    def remove_from_list_via_list(self, remove_from: list, remove_with: list) -> list:
        """
        This function takes a list and removes any items from it that exist in
        another list.

        Args:
            remove_from (list): The list that we want to remove items from.
            remove_with (list): The list containing the items we want to remove
                from the other list.
        Returns:
            transformed_list (list): The list with remaining items.
        """
        transformed_list = [x for x in remove_from if x not in remove_with]
        return transformed_list


class AllRecipes(Scraper):

    def __init__(self) -> None:
        """
        Set up the Scraper to work for AllRecipes.com. Visit the
        intial search page and accept cookies.

        Intialise the options required to support use of the scraper for this
        site.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('— disk-cache-size=0')
        options.add_argument("no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")

        super().__init__(
            'https://www.allrecipes.com/search/results/?search=',
            options
            )
        self.accept_cookies('//*[@id="onetrust-accept-btn-handler"]', None)

    def scrape_links_from_search_page(self, scrape_count: int) -> list:
        """
        This function infinitely scrolls and collects a list of links up to
        the number specified.

        Args:
            scrape_count (int): The number of links the user wants to screape
                from.
        """
        links_length = 0
        # progress bar creations
        pbar = tqdm(desc='Scraping links...', total=scrape_count)
        # Build list of links by scrolling until scrape count is reached
        while links_length < scrape_count:
            # Get list of links after one scroll
            links = []
            links.extend(self.scrape_page_links(
                '//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',
                1
            ))
            # Remove links already scraped
            links = self.remove_from_list_via_list(links, self.scraped_ids)
            # Calculate number of links scraped after removal of those already scraped.
            # If the number of links scraped is lower than required repeat.
            links_length = len(links)
            # Update progress bar with the number of links scraped so far.
            pbar.update(links_length)
        # Reduce the number of links down to be exactly the number specified by the user.
        links = links[:scrape_count]
        return links

    def scrape_from_recipe_page(self, link: str) -> dict:
        """
        This functions goes too and scraped recipe data for each link.

        The function visits each link and begings scraping the required data.
        If the user wnats more data from the webpage this can be updated.
        This creates a dictionary for each link.

        Args:
            link (str): The url to scrape from.
        Retruns:
            recipe_dict (dict): The disctionary with all scraped data for the
                recipe.
        """
        self.driver.get(link)
        recipe_dict = {
            'recipe_uuid4': self.generate_uuid4(),
            'recipe_id': self.extract_continous_digit_group(link),
            'link': link,
            }
        scraped_page_dict = self.scrape_multiple_page_elements(
            ingredient_list='//span[@class="ingredients-item-name elementFont__body"]',
            recipe_meta='//div[@class="recipe-meta-item"]',
            direction_steps='//span[@class="checkbox-list-text elementFont__subtitle--bold"]',
            directions_instructions='//div[@class="section-body elementFont__body--paragraphWithin elementFont__body--linkWithin"]/div[@class="paragraph"]/p',
            nutrition_summary='//div[@class="section-body"]',
            sub_categories='//span[@class="breadcrumbs__title"]'
            )
        recipe_dict.update(scraped_page_dict)
        return recipe_dict

    def create_image_upload_directory(self, recipe_dict: dict) -> str:
        """
        This function creates the folder strucutre for uploading the recipe
        data for AllRecipes.

        The function scrapes the sub-categories that ar eused by the
        website for each recipe. The final sub-category with be prefixed
        with AllRecipes and then either the first two categories or the last
        category is selected.

        Args:
            recipe_dict (dict): The dictionary with the recipe data, including
                the sub-categories.
        Returns:
            sub_cat (str): A string with / to specific directory or catgeories
                for the recipe
        """
        try:
            sub_cat = os.path.join("AllRecipes", re.sub(r'\W+', '', recipe_dict['sub_categories'][2]))
        except IndexError:
            sub_cat = os.path.join("AllRecipes", re.sub(r'\W+', '', recipe_dict['sub_categories'][-1]))
        return sub_cat

    def create_recipe_dataframe(self, recipe_dict: dict) -> pd.DataFrame:
        """
        This function creates the dataframe where one does not already exist,
        based on the dictionary.

        Args:
            recipe_dict (dict): The dictionary with the scraped recipe data.
        Returns:
            recipe_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            ingredients_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            directions_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            recipe_meta_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            nutrition_summary_df (pd.DataFrame): The dataframe with the
            spefified dictionary values for this data.
            image_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
        """
        image_id = self.generate_uuid4()
        recipe_df_create = self.create_df_from_dict(['recipe_uuid4', 'recipe_id', 'link'], recipe_dict)
        ingredients_df_create = self.create_df_from_dict(['recipe_uuid4', 'ingredient_list'], recipe_dict)
        directions_df_create = self.create_df_from_dict(['recipe_uuid4', 'direction_steps', 'directions_instructions'], recipe_dict)
        recipe_meta_df_create = self.create_df_from_dict(['recipe_uuid4', 'recipe_meta'], recipe_dict)
        nutrition_summary_df_create = self.create_df_from_dict(['recipe_uuid4', 'nutrition_summary'], recipe_dict)
        image_df_create = pd.DataFrame([{
                'image_id': image_id,
                'recipe_id': recipe_dict['recipe_uuid4'],
                'image_link': f"https://watsonaicore.s3.amazonaws.com/{self.create_image_upload_directory(recipe_dict)}/{image_id}"
                }])
        recipe_df = recipe_df_create
        ingredients_df = ingredients_df_create
        directions_df = directions_df_create
        recipe_meta_df = recipe_meta_df_create
        nutrition_summary_df = nutrition_summary_df_create
        image_df = image_df_create
        return recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df

    def extend_recipe_dataframe(self, recipe_dict: dict, recipe_df: pd.DataFrame, ingredients_df: pd.DataFrame, directions_df: pd.DataFrame, recipe_meta_df: pd.DataFrame, nutrition_summary_df: pd.DataFrame, image_df: pd.DataFrame):
        """
        This function extends the dataframe where one does not already exist,
        based on the dictionary.

        Args:
            recipe_dict (dict): The dictionary with the scraped recipe data.
            recipe_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data that was already created.
            ingredients_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data that was already created.
            directions_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data that was already created.
            recipe_meta_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data that was already created.
            nutrition_summary_df (pd.DataFrame): The dataframe with the
            spefified dictionary values for this data that was already created.
            image_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data that was already created.
        Returns:
            recipe_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            ingredients_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            directions_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            recipe_meta_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
            nutrition_summary_df (pd.DataFrame): The dataframe with the
            spefified dictionary values for this data.
            image_df (pd.DataFrame): The dataframe with the spefified
            dictionary values for this data.
        """
        image_id = self.generate_uuid4()
        recipe_df_create = self.create_df_from_dict(['recipe_uuid4', 'recipe_id', 'link'], recipe_dict)
        ingredients_df_create = self.create_df_from_dict(['recipe_uuid4', 'ingredient_list'], recipe_dict)
        directions_df_create = self.create_df_from_dict(['recipe_uuid4', 'direction_steps', 'directions_instructions'], recipe_dict)
        recipe_meta_df_create = self.create_df_from_dict(['recipe_uuid4', 'recipe_meta'], recipe_dict)
        nutrition_summary_df_create = self.create_df_from_dict(['recipe_uuid4', 'nutrition_summary'], recipe_dict)
        image_df_create = pd.DataFrame([{
                'image_id': image_id,
                'recipe_id': recipe_dict['recipe_uuid4'],
                'image_link': f"https://watsonaicore.s3.amazonaws.com/{self.create_image_upload_directory(recipe_dict)}/{image_id}"
                }])
        recipe_df = pd.concat([recipe_df, recipe_df_create])
        ingredients_df = pd.concat([ingredients_df, ingredients_df_create])
        directions_df = pd.concat([directions_df, directions_df_create])
        recipe_meta_df = pd.concat([recipe_meta_df, recipe_meta_df_create])
        nutrition_summary_df = pd.concat([nutrition_summary_df, nutrition_summary_df_create])
        image_df = pd.concat([image_df, image_df_create])
        return recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df
