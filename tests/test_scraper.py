from gettext import find
from scraper_folder.scraper import Scraper
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
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
        self.bot = Scraper('https://www.allrecipes.com/search/results/?search=')

    # def test_activate_driver(self):
    #     # Check driver is going to the url that was provided
    #     expected_value = 'https://www.allrecipes.com/search/results/?search='
    #     actual_value = self.bot.driver.current_url
    #     self.assertEqual(expected_value, actual_value)

    # def test_accept_cookies(self):
    #     # find the element
    #     # accept the element
    #     # element should no longer be found
    #     self.bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]')
    #     with self.assertRaises(ElementNotInteractableException):
    #         self.bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]')
    
    # def test_perform_search_with_bar(self):
    #     expected_value = 'https://www.allrecipes.com/search/results/?search=vegan+berry'
    #     self.bot.perform_search_with_bar('//input[@id="primary-search"]', 'vegan berry')
    #     actual_value = self.bot.driver.current_url
    #     self.assertEqual(expected_value, actual_value)

    # def test_scrape_element(self):
    #     expected_value = 'Recipe Results'
    #     actual_value = self.bot.scrape_element('//h1[@id="search-results-heading"]')
    #     self.assertEqual(expected_value, actual_value)

    # def test_scrape_page_elements(self):
    #     expected_value = ['Recipe or keyword', 'Ingredients']
    #     actual_value = self.bot.scrape_page_elements('//label[@class="faceted-search-filters-available-input-label elementFont__body--bold"]')
    #     self.assertEqual(expected_value, actual_value)

    def test_scrape_multiple_page_elements(self):
        expected_value = {
            'ingredient_list' : ['2 large cucumbers, peeled, halved lengthwise, seeds scraped out, then thinly sliced',
                                    '1 teaspoon salt', 
                                    '¼ medium red onion, thinly sliced',
                                    '6 tablespoons sour cream', 
                                    '1 tablespoon red wine vinegar', 
                                    '½ teaspoon dried dill', 
                                    'Ground black pepper', 
                                    '4 (5 ounce) salmon fillets', 
                                    'Olive oil'], 
            'recipe_meta' : ['Servings: 4', 'Yield: 4 servings'], 
            'direction_steps' : ['Step 1', 'Step 2', 'Step 3'],
            'directions_instructions' : ['Place cucumbers in a colander and toss with salt; let stand until several tablespoons of liquid has drained, 30 to 45 minutes. Pat dry with paper towels and transfer to a medium bowl. Add onion, sour cream, vinegar, dill and a few grinds of pepper. Toss to coat. (Can be refrigerated several hours ahead.)', 
                                            'Meanwhile, heat gas grill, with all burners on high, until fully preheated, 10 to 15 minutes. Use a wire brush to clean grill rack, then brush lightly with oil. Close lid and let return to temperature. Brush salmon with oil and season with salt and pepper; grill until just opaque, about 3 minutes per side.', 
                                            'Set each warm or room-temperature salmon fillet on a plate; spoon cucumber salad over part of and alongside the fish.'
                                        ],
            'nutrition_summary' : ['362 calories; protein 30g; carbohydrates 7.2g; fat 23.5g; cholesterol 93.3mg; sodium 680.1mg. Full Nutrition']
        }
        self.bot.driver.get('https://www.allrecipes.com/recipe/76967/grilled-salmon-with-cucumber-salad/')
        actual_value =  self.bot.scrape_multiple_page_elements(
            ingredient_list='//span[@class="ingredients-item-name elementFont__body"]', 
            recipe_meta='//div[@class="recipe-meta-item"]',
            direction_steps='//ul[@class="instructions-section"]/li[@class="subcontainer instructions-section-item"][*]/label[@class="checkbox-list"]',
            directions_instructions='//div[@class="section-body elementFont__body--paragraphWithin elementFont__body--linkWithin"]/div[@class="paragraph"]/p',
            nutrition_summary= '//div[@class="section-body"]'
            )
        self.assertEqual(expected_value, actual_value)

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

    # def create_json(self):
    # def test_get_root_path(self):
    # def test_extract_continous_digit_group(self):

    #def tearDown(self):
        # this is used to remove ny of the variables set up from memory
        # del self.bot

# This makes sure all tests are run
# exit, prevents the kernel restarting after test so that it does not have to rerun the tests each time
# argv can parse agruments to the test using the command line
if __name__ == "__main__":
    unittest.main(verbosity=3, exit=False)