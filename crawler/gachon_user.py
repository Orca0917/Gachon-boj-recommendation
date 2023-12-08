"""
Crawling user information from Gachon University

Targets students of Gachon University on Baekjoon Online Judge,
to identify the list of problems they have solved and their tier information.
"""

import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    # Chrome driver options (to run headlessly)
    driver_option = webdriver.ChromeOptions()
    driver_option.add_argument('headless')

    # Launching Chrome driver
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)

    # List to store crawled information
    user_data = []

    # Accessing the ranking page
    driver.get('https://www.acmicpc.net/school/ranklist/187')
    time.sleep(3)

    # Determining the maximum number of pages
    page_elem = driver.find_elements(by=By.XPATH, value="(//ul[@class='pagination']/li/a)[position()>1]")
    MAX_PAGE = max([int(elem.get_attribute('href').split("/")[-1]) for elem in page_elem])

    # Looping through each page
    for page in tqdm(range(MAX_PAGE)):
        driver.get(f'https://www.acmicpc.net/school/ranklist/187/{page + 1}')
        time.sleep(3)

        # Extracting Gachon University student usernames on current page
        gachon_user_elem = driver.find_elements(by=By.CSS_SELECTOR, value='#ranklist > tbody > tr > td:nth-child(2) > a')
        user_list = [user_elem.get_attribute('href').split("/")[-1] for user_elem in gachon_user_elem]

        # Progress bar for user list
        pbar = tqdm(user_list, leave=False)
        for user_name in pbar:
            # Accessing each user's Baekjoon information page
            driver.get(f'https://www.acmicpc.net/user/{user_name}')
            
            # Waiting for user's tier information to appear
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[@class='page-header']/h1"))
            )

            # Waiting for user's problem-solving history to appear
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'panel') and contains(@class, 'panel-default') and .//h3[contains(text(), '맞은 문제')]]//a"))
            )

            # Extracting user's tier information
            user_tier = None
            try:
                solvedac_tier_img_tag = driver.find_element(by=By.XPATH, value="//*[@class='page-header']/h1/a/img")
                solvedac_tier_tag_src = solvedac_tier_img_tag.get_attribute('src').split("/")[-1]
                solvedac_tier_num = int(solvedac_tier_tag_src.split(".")[0])
                pbar.set_postfix(name=user_name, tier=solvedac_tier_num, refresh=True)
                user_tier = 0 if solvedac_tier_num == -1 else solvedac_tier_num
            except:
                user_tier = 0
                
            # Extracting problems solved by the user
            solved_problems = driver.find_elements(by=By.XPATH, value="//div[contains(@class, 'panel') and contains(@class, 'panel-default') and .//h3[contains(text(), '맞은 문제')]]//a")
            for solved in solved_problems:
                user_data.append([user_name, solved.text, user_tier])

finally:
    # Closing the driver
    driver.quit()

# Saving data to a CSV file
column_name = ['userName', 'problemId', 'userTier']
gachon_user_df = pd.DataFrame(data=user_data, columns=column_name)
gachon_user_df.to_csv("./gachon_user_data.csv", index=False)
