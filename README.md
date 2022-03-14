# recipe_webscraper

recipe_webscraper is a python package for extracting data specified by the user from a website. It has been developed to scrape recipes from https://www.allrecipes.com/ but can be used universally where the functions included fit the format of your website. Addittional development may be required to fit the website you are scraping from.

It uses the selenium as the main tool for navigating and scraping webpages.

## Feature list
The Scraper class includes the following features delivered through class methods (see Usage section to find out more about these methods). The name of the method is provided in parenthesis:

* Intialisation of:
    * Chrome web driver
    * S3 client
    * RDS engine
* Create JSON from dictionary (create_json)
* Idenify root path of project (get_root_path)
* Extract continous string of numbers from a string e.g. a URL. (extract_continous_digit_group) 
* Accept cookies button press (accept_cookies)
* Run search with search bar (perform_search_with_bar)
* Scrape individual element via xpath (scrape_element)
* Scrape list of elements via x path (scrape_page_elements)
* Scrape dynamic list of elements via xpath (scrape_multiple_page_elements)
* Navigate to a specific URL (navigate_to)
* Scroll to page end (scroll_page)
* Infinite scroll (scroll_infinite)
* Infinite scroll and scrape list of elements via xpath (scrape_page_links)
* Generate a uuid4 (generate_uuid4)
* Download image to local directory via xpath (download_image)
* Upload image to S3 bucket (upload_image)
* Create local directory  (create_directory)
* Upload local directory to S3 bucket  (upload_directory)


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the webscraper.

```bash
pip install recipe_webscraper
```

## Usage

```python
import scraper
import os

# intialises Chrome webdriver as bot and opens the URL page
URL = 'https://www.allrecipes.com/search/results/?search='
bot = Scraper(URL)

# Creates json file named data into the root path of the project
recipe_dict = {
    'recipe_uuid4': '8d007e0b-677d-46f8-8cfa-0ce0be943dbf',
    'recipe_id': '255343',
    'link': 'https://www.allrecipes.com/recipe/255343/best-vegan-chocolate-oatmeal-waffles/'
    }
root_path = os.getcwd()
bot.create_json(root_path, 'data.json', recipe_dict)

# returns string of root path for current file like '/home/Documents/webscraper'
bot.get_root_path()

# returns string '166727'
bot.extract_continous_digit_group('https://www.allrecipes.com/recipe/166727/donnas-123-sausage-balls/')

# clicks button specified in the xpath
bot.accept_cookies('//*[@id="onetrust-accept-btn-handler"]')

# types 'vegan berry' in search bar and clicks search to navigate to the search results from the website
bot.perform_search_with_bar('//input[@id="primary-search"]', 'vegan berry')

# returns string 'Recipe Results' if used directly after intialising Scraper class, like above. Note xpath may change and result may differ
bot.scrape_element('//h1[@id="search-results-heading"]')

# returns a list of strings like ['Recipe or keyword', 'Ingredients']. This example is based on intilising the Scraper class like above. Note the x path may have changed.
bot.scrape_page_elements('//label[@class="faceted-search-filters-available-input-label elementFont__body--bold"]')

# returns a dictionary with a list of elements for each argument parsed by user like below: 
    # {
    #   'recipe_meta': ['Servings: 4', 'Yield: 4 servings'],
    #   'direction_steps': ['Step 1', 'Step 2', 'Step 3']
    # }
bot.driver.get('https://www.allrecipes.com/recipe/76967/grilled-salmon-with-cucumber-salad/')
bot.scrape_multiple_page_elements(
            recipe_meta='//div[@class="recipe-meta-item"]',
            direction_steps='//ul[@class="instructions-section"]/li'
)

# opens the url found via x path
bot.navigate_to('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]', 'href')

# scrolls to bottom of page once. if there is infinite scroll then use infinite scroll
bot.scroll_page()

# scrolls to bottom of webpage 3 times
bot.scroll_infinite(3)

# returns list of url's like ['https://www.allrecipes.com/recipe/246450/spicy-watercress-salad/','https://www.allrecipes.com/recipe/240419/aidan-special']
bot.scrape_page_links('//a[@class="card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"]',
     1)

# returns a random string following uuid4 standard like c8d27d74-bd3e-45b6-97d2-812c66b38d13
bot.generate_uuid4()

# downloads image file named 'image_file.jpg' to root path of the project you are working based on xpath provided.
bot.download_image('//div[@class="inner-container js-inner-container image-overlay"]/img', os.path.join(os.getcwd(), 'image_file.jpg'))

# Uploads file named 'image_file.jpg' to s3 bucket named 'S3_BUCKET' in a folder named 'image_folder' (not the / in the final arugment creates the folder structure)
bot.upload_image('//div[@class="inner-container js-inner-container image-overlay"]/img', 'image_file.jpg' , 'S3_BUCKET', 'image_folder/image_file.jpg')

# creates a local directory named 'raw_data' to the root path of the project
bot.create_directory('raw_data', bot.get_root_path())

# Uploads a your projects local root directory to an s3 bucket named 'S3_BUCKET' following the same folder struture as you have locally.
bot.upload_directory(os.getcwd(), 'S3_BUCKET')

```
## Roadmap
The following are planned developments:
* Prevent error if RDS table for recipes does not already exist
* Include progress bar for infinite scroll
* Amend max scroll argument to request for number of links to scrape. This will enable user more flexibility
* Add ability to download multiple images
* Add class for allrecipes.com for scraping
* Add class for at least one other recipe website - others to follow
* Scrape more data that will be useful e.g. review score a comments

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
