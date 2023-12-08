import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By

try:
    # Setting Chrome driver options to run in headless mode
    driver_option = webdriver.ChromeOptions()
    driver_option.add_argument('headless')
    
    # Initializing the Chrome driver
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)  # Setting implicit wait

    # Maximum level for crawling
    MAX_LEVEL = 30
    # Lists to store problem tier data and any failed levels or pages
    problem_tier_data, level_failed, page_failed = [], [], []

    # Iterating over each level
    for level in tqdm(range(MAX_LEVEL), desc='LEVEL crawling'):
        driver.get(f'https://solved.ac/problems/level/{level + 1}')
        time.sleep(3)  # Sleep to ensure the page loads

        # Fetching problem information
        page_elem = driver.find_elements(by=By.CSS_SELECTOR, value='.css-18lc7iz > a')
        # If no elements are found, record the failed level
        if len(page_elem) == 0:
            level_failed.append(f"level-{level}")
        # Determining the maximum page number for the current level
        MAX_PAGE = max([int(elem.get_attribute('href').split("=")[-1]) for elem in page_elem])

        # Iterating over each page in the current level
        for page in tqdm(range(MAX_PAGE), desc='Page crawling', leave=False):
            driver.get(f'https://solved.ac/problems/level/{level + 1}?page={page + 1}')
            time.sleep(3)  # Sleep to ensure the page loads

            # Fetching problem elements on the current page
            problem_elem = driver.find_elements(by=By.CSS_SELECTOR, value='.css-lywkv4 > span > a')
            # If no problem elements are found, record the failed page
            if len(problem_elem) == 0:
                page_failed.append(f"level-{level}-page-{page}")

            # Extracting problem IDs and their levels
            for elem in problem_elem:
                problem_tier_data.append([int(elem.get_attribute('href').split("/")[-1]), level])

finally:
    # Quitting the driver after completing the crawl
    driver.quit()

# Creating a DataFrame with problem IDs and their tiers
column_name = ['problemId', 'tier']
pd.DataFrame(data=problem_tier_data, columns=column_name).to_csv("./problem_tier_data.csv", index=False)
