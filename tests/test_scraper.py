from scraper_folder.scraper import Scraper
import unittest
# unit testing ideas:
# 1. Check that the uuid4 does not duplicate
# 2. Check it gets the images for each, could probaly att wait for element to my functions for safety
# 3. Add extra element in does it still work
# 4. Change website, does it still work
# 5. If there is a duplicate id will it error
# 6. Does the data scraped match the expected values (foudn it doesn't seem to line 1/4 or brackets like (12 Ounce))
# 7. using find elements when there is only one element in the multiple scraper - does it still work?
# 8. Try with Firefox?

class ScraperTestCase(unittest.TestCase):

    def setUp(self):
        # this is used to set up any variables that will be used in the tests.
        self.home_page = Scraper('https://www.allrecipes.com/search/results/?search=')
        self.recipe_page = Scraper('https://www.allrecipes.com/recipe/219900/jeris-spicy-buffalo-wings/')

    def test_activate_driver(self):
        # Check driver is going to the url that was provided
        expected_value = 'https://www.allrecipes.com/search/results/?search='
        actual_value = self.home_page
        self.assertEqual(expected_value, actual_value)

    # def test_accept_cookies(self):
    #     # accept_cookies
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)
    
    # def test_perform_search_with_bar(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_scrape_element(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_scrape_page_elements(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_scrape_multiple_page_elements(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_navigate_to(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_scroll_page(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_scroll_infinite(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_scrape_page_links(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_generate_uuid4(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_download_image(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    # def test_create_directory(self):
    #     expected_value = 'x'
    #     actual_value = 'y'
    #     self.assertEqual(expected_value, actual_value)

    def tearDown(self):
        # this is used to remove ny of the variables set up from memory
        del self.home_page
        del self.recipe_page

# This makes sure all tests are run
# exit, prevents the kernel restarting after test so that it does not have to rerun the tests each time
# argv can parse agruments to the test using the command line
unittest.main(exit=False)