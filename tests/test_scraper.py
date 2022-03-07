from scraper_folder.scraper import Scraper
from selenium.common.exceptions import ElementNotInteractableException
import unittest
import os
import boto3
from moto import mock_s3



class ScraperTestCase(unittest.TestCase):

    def setUp(self):
        # this is used to set up any variables that will be used in the tests.
        self.bot = Scraper('https://www.allrecipes.com/search/results/?search=')
        self.client = boto3.client(
            "s3",
            region_name="eu-west-1",
            aws_access_key_id="fake_access_key",
            aws_secret_access_key="fake_secret_key",
            )

    def test_activate_driver(self):
        # Check driver is going to the url that was provided
        expected_value = 'https://www.allrecipes.com/search/results/?search='
        actual_value = self.bot.driver.current_url
        self.assertEqual(expected_value, actual_value)

    def test_accept_cookies(self):
        # find the element
        # accept the element
        # element should no longer be found
        self.bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]')
        with self.assertRaises(ElementNotInteractableException):
            self.bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]')

    def test_perform_search_with_bar(self):
        expected_value = 'https://www.allrecipes.com/search/results/?search=vegan+berry'
        self.bot.perform_search_with_bar('//input[@id="primary-search"]', 'vegan berry')
        actual_value = self.bot.driver.current_url
        self.assertEqual(expected_value, actual_value)

    def test_scrape_element(self):
        expected_value = 'Recipe Results'
        actual_value = self.bot.scrape_element('//h1[@id="search-results-heading"]')
        self.assertEqual(expected_value, actual_value)

    def test_scrape_page_elements(self):
        expected_value = ['Recipe or keyword', 'Ingredients']
        actual_value = self.bot.scrape_page_elements('//label[@class="faceted-search-filters-available-input-label elementFont__body--bold"]')
        self.assertEqual(expected_value, actual_value)

    def test_scrape_multiple_page_elements(self):
        expected_value = {
            'ingredient_list': ['2 large cucumbers, peeled, halved lengthwise, seeds scraped out, then thinly sliced',
                                '1 teaspoon salt',
                                '\u00BC medium red onion, thinly sliced',
                                '6 tablespoons sour cream',
                                '1 tablespoon red wine vinegar',
                                '\u00BD teaspoon dried dill',
                                'Ground black pepper',
                                '4 (5 ounce) salmon fillets',
                                'Olive oil'],
            'recipe_meta': ['Servings: 4', 'Yield: 4 servings'],
            'direction_steps': ['Step 1', 'Step 2', 'Step 3'],
            'directions_instructions': ['Place cucumbers in a colander and toss with salt; let stand until several tablespoons of liquid has drained, 30 to 45 minutes. Pat dry with paper towels and transfer to a medium bowl. Add onion, sour cream, vinegar, dill and a few grinds of pepper. Toss to coat. (Can be refrigerated several hours ahead.)', 
                                        'Meanwhile, heat gas grill, with all burners on high, until fully preheated, 10 to 15 minutes. Use a wire brush to clean grill rack, then brush lightly with oil. Close lid and let return to temperature. Brush salmon with oil and season with salt and pepper; grill until just opaque, about 3 minutes per side.', 
                                        'Set each warm or room-temperature salmon fillet on a plate; spoon cucumber salad over part of and alongside the fish.'
                                        ],
            'nutrition_summary': ['362 calories; protein 30g; carbohydrates 7.2g; fat 23.5g; cholesterol 93.3mg; sodium 680.1mg. Full Nutrition']
        }
        self.bot.driver.get('https://www.allrecipes.com/recipe/76967/grilled-salmon-with-cucumber-salad/')
        actual_value = self.bot.scrape_multiple_page_elements(
            ingredient_list='//span[@class="ingredients-item-name elementFont__body"]',
            recipe_meta='//div[@class="recipe-meta-item"]',
            direction_steps='//ul[@class="instructions-section"]/li[@class="subcontainer instructions-section-item"][*]/label[@class="checkbox-list"]',
            directions_instructions='//div[@class="section-body elementFont__body--paragraphWithin elementFont__body--linkWithin"]/div[@class="paragraph"]/p',
            nutrition_summary='//div[@class="section-body"]'
            )
        self.assertEqual(expected_value, actual_value)

    def test_navigate_to(self):
        # This gets the recipe name for the first recipe on the search page
        expected_value = self.bot.scrape_element('//h3[@class="card__title elementFont__resetHeading"]')
        # This navigates to the first recipe on the search page
        self.bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')
        # This gets the recipe name from the specified recipe page which should be the same as the expected value
        actual_value = self.bot.scrape_element('//h1[@class="headline heading-content elementFont__display"]')
        self.assertEqual(expected_value, actual_value)

    def test_scroll_page(self):
        not_expected_value = self.bot.driver.execute_script("return document.body.scrollHeight")
        self.bot.scroll_page()
        actual_value = self.bot.driver.execute_script("return document.body.scrollHeight")
        self.assertNotEqual(not_expected_value, actual_value)

    def test_scroll_infinite(self):
        not_expected_value = self.bot.driver.execute_script("return document.body.scrollHeight")
        self.bot.scroll_infinite(2)
        actual_value = self.bot.driver.execute_script("return document.body.scrollHeight")
        self.assertNotEqual(not_expected_value, actual_value)

    def test_scrape_page_links(self):
        # Check can find the start of the url in each item of the list
        expected_value = True
        links = self.bot.scrape_page_links(
            '//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',
            1
            )
        actual_value = all('https://www.allrecipes.com/recipe' in link for link in links)
        self.assertEqual(expected_value, actual_value)

    def test_generate_uuid4(self):
        expected_length = 36
        id_generated = self.bot.generate_uuid4()
        actual_length = len(id_generated)
        self.assertEqual(expected_length, actual_length)

    def test_download_image(self):
        file = 'test_image'
        # # File location
        root_path = os.getcwd()
        # # Path
        path = os.path.join(root_path, file)
        # # Remove the file
        # # 'test_image'
        if 'test_image' in os.listdir():
            os.remove(path)
        self.bot.driver.get('https://www.allrecipes.com/recipe/282185/martina-mcbrides-kansas-creamy-mashed-potatoes/')
        downloaded_image = self.bot.download_image('//div[@class="inner-container js-inner-container image-overlay"]/img', file)
        actual_value = 'test_image' not in os.listdir()
        if downloaded_image == 'No image downloaded':
            self.assertTrue(actual_value)
        else:
            self.assertTrue(actual_value)
            os.remove(path)

    def test_create_directory(self):
        directory_name = 'test_directory'
        # # File location
        root_path = os.getcwd()
        # # Path
        path = os.path.join(root_path, directory_name)
        if 'test_directory' in os.listdir():
            os.rmdir(path)
        expected_value = True
        self.bot.create_directory(directory_name, root_path)
        actual_value = 'test_directory' in os.listdir()
        self.assertEqual(expected_value, actual_value)
        os.rmdir(path)

    def test_create_json(self):
        file = 'test_json'
        # # File location
        root_path = os.getcwd()
        # # Path
        path = os.path.join(root_path, file)
        if 'test_json' in os.listdir():
            os.remove(path)
        test_dict = {
            'test_line_1': 'This is the first test',
            'test_line_2': 2
            }
        self.bot.create_json(os.getcwd(), file, test_dict)
        expected_value = True
        actual_value = 'test_json' in os.listdir()
        self.assertEqual(expected_value, actual_value)
        os.remove(path)

    def test_get_root_path(self):
        expected_value = os.getcwd()
        actual_value = self.bot.get_root_path()
        self.assertEqual(expected_value, actual_value)

    def test_extract_continous_digit_group(self):
        expected_value = '166727'
        self.bot.driver.get('https://www.allrecipes.com/recipe/166727/donnas-123-sausage-balls/')
        actual_value = self.bot.extract_continous_digit_group('https://www.allrecipes.com/recipe/166727/donnas-123-sausage-balls/')
        print(actual_value)
        self.assertEqual(expected_value, actual_value)

    @mock_s3
    def test_upload_directory():


    def tearDown(self):
        # this is used to remove any of the variables set up from memory
        del self.bot

# This makes sure all tests are run
# exit, prevents the kernel restarting after test so that it does not have to rerun the tests each time
# argv can parse agruments to the test using the command line


if __name__ == "__main__":
    unittest.main(verbosity=3, exit=False)
