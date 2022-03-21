from scraper import AllRecipes
from scraper import tqdm


bot = AllRecipes()
links = bot.scrape_links_from_search_page(10)
count = 0
for link in tqdm(links, desc='Scraping pages...'):
    recipe_dict = bot.scrape_from_recipe_page(link)
    if recipe_dict['recipe_id'] not in bot.scraped_ids:
        if count == 0:
            recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df = bot.create_recipe_dataframe(recipe_dict)
        else:
            recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df = bot.extend_recipe_dataframe(recipe_dict, recipe_df, ingredients_df, directions_df, recipe_meta_df, nutrition_summary_df, image_df)
        # self.upload_image('//div[@class="inner-container js-inner-container image-overlay"]/img', image_id , 'watsonaicore', sub_cat)
        count += 1
# Upload to RDS
# image_df.to_sql('image', bot.engine, if_exists='append')
# recipe_df.to_sql('recipe', bot.engine, if_exists='append')
# directions_df.to_sql('directions', bot.engine, if_exists='append')
# ingredients_df.to_sql('ingredients', bot.engine, if_exists='append')
# recipe_meta_df.to_sql('recipe_meta', bot.engine, if_exists='append')
# nutrition_summary_df.to_sql('nutrition', bot.engine, if_exists='append')
print(recipe_df)
print(ingredients_df)
