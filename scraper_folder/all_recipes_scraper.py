from scraper_folder.scraper import AllRecipes
from scraper_folder.scraper import tqdm

bot = AllRecipes()
links = bot.scrape_links_from_search_page(2)
count = 0
for link in tqdm(links, desc='Scraping pages...'):
    recipe_dict = bot.scrape_from_recipe_page(link)
    if count == 0:
        recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df = bot.create_recipe_dataframe(recipe_dict)
    else:
        recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df = bot.extend_recipe_dataframe(recipe_dict, recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df)
    count += 1
# Just need to include upload 
print(recipe_df)
print(ingredients_df)
