import time
import pandas as pd
from tqdm.notebook import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By

# Dictionary mapping tiers to their starting pages
tier_start_page = {
    # Tier mappings, e.g., '31': 1 (master tier starts at page 1)
    '31': 1, # master
    '30': 1, # ruby 1
    '29': 1, # ruby 2
    '28': 1, # ruby 3
    '27': 2, # ruby 4
    '26': 2, # ruby 5
    '25': 3, # diamond 1
    '24': 5, # diamond 2
    '23': 7, # diamond 3
    '22': 10, # diamond 4
    '21': 14, # diamond 5
    '20': 21, # platinum 1
    '19': 27, # platinum 2
    '18': 35, # platinum 3
    '17': 47, # platinum 4
    '16': 79, # platinum 5
    '15': 140, # gold 1
    '14': 300, # gold 2
    '13': 400, # gold 3
    '12': 500, # gold 4
    '11': 700, # gold 5
    '10': 800, # silver 1
    '9': 1000, # silver 2
    '8': 1100, # silver 3
    '7': 1200, # silver 4
    '6': 1400, # silver 5
    '5': 1800, # bronze 1
    '4': 1900, # bronze 2
    '3': 2000, # bronze 3
    '2': 2100, # bronze 4
    '1': 2200, # bronze 5
}

try:
    # Setting up Chrome driver for headless browsing
    driver_option = webdriver.ChromeOptions()
    driver_option.add_argument('headless')

    # Initializing the Chrome driver
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)  # Implicit wait for elements to load

    # List to store crawled data
    crawled_300_user_by_tier = []

    # Constant to limit number of users crawled per tier
    COUNT = 300

    # Progress bar for tiers
    tqdm_bar = tqdm(range(31, 0, -1))
    for tier in tqdm_bar:
        tier_str = str(tier)
        tier_cnt, page = 0, tier_start_page[tier_str]

        while True:
            # Accessing the page for each tier
            driver.get(f'https://solved.ac/ranking/tier?page={page}')
            time.sleep(3)  # Delay for page load

            # Extracting user names and tiers
            user_name_list = driver.find_elements(by=By.CSS_SELECTOR, value='span > a > b')
            user_tier_list = driver.find_elements(by=By.XPATH, value='//*[@id="__next"]/div[5]/div[1]/table/tbody/tr/td[2]/span/a/img[1]')

            # Parsing extracted data
            user_name_list = [user_name.text for user_name in user_name_list]
            user_tier_list = [user_tier.get_attribute('src')[:-4].split("/")[-1] for user_tier in user_tier_list]

            # Break if lower tier users start appearing
            if int(user_tier_list[0]) < int(tier_str):
                break

            # Collecting data for users in the current tier
            for cur_name, cur_tier in zip(user_name_list, user_tier_list):
                if cur_tier == tier_str and tier_cnt < COUNT:
                    tier_cnt += 1
                    tqdm_bar.set_postfix(tier=tier_str, page=page, counts=tier_cnt, refresh=True)
                    crawled_300_user_by_tier.append([cur_tier, cur_name])

            # Break if 300 users for the tier have been crawled
            if tier_cnt == COUNT:
                break

            page += 1
finally:
    print("Chrome driver가 정상적으로 종료되었습니다.")  # Message indicating driver closure
    driver.quit()  # Closing the driver

# Saving the crawled data to a CSV file
column_name = ['tier', 'userId']
gachon_user_df = pd.DataFrame(data=crawled_300_user_by_tier, columns=column_name)
gachon_user_df.to_csv("./300_tier_data.csv", index=False)
