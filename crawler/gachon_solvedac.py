import time
import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Maximum number of pages to scrape
MAX_PAGE = 7
# List to store user information
user_information = []
# List of tags to be scraped
tags = [
    'math',
    'implementation',
    'greedy',
    'string',
    'data_structures',
    'graphs',
    'dp',
    'geometry'
]

try:
    # Setting up the Chrome driver for Selenium
    driver_option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)  # Implicit wait of 3 seconds

    # Looping through pages
    for page in tqdm(range(1, MAX_PAGE + 1)):
        driver.get(f'https://solved.ac/ranking/o/187?page={page}')
        time.sleep(3)  # Delay to ensure page loads

        # Scraping user names
        userNames = driver.find_elements(by=By.XPATH, value="//tr[@class='css-1ojb0xa']/td[3]/span/a/b")
        userNames = [elem.text for elem in userNames]

        # Looping through each user
        for idx, userName in enumerate(userNames):
            driver.get(f'https://solved.ac/profile/{userName}')
            time.sleep(3)
            status = []

            # Expanding 'more tags' section
            while True:
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div[3]/div/div[8]/div[3]/div[3]"))
                    )
                    button = driver.find_element(By.XPATH, "//*[@id='__next']/div[3]/div/div[8]/div[3]/div[3]")
                    button.click()
                except TimeoutException:
                    print(f"[DEBUG] Page #{page}-{idx} no more 'More' button exists.")
                    break

            # Scraping scores for each tag
            for tag in tags:
                try:
                    stat = driver.find_element(by=By.XPATH, value=f"//a[contains(@href, '{tag}')]/../../../td[4]/b/span")
                    status.append(int(stat.text.split(" ")[-1]))
                except NoSuchElementException:
                    print(f"[DEBUG] Current user {userName} does not have a solution history for algorithm tag #{tag}")
                    status.append(0)

            # Appending user information
            user_information.append([userName] + status)

finally:
    # Closing the driver
    driver.quit()

# Defining column names for DataFrame
column_name = ['userName', 'tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8']
# Creating DataFrame from the scraped data
problem_df = pd.DataFrame(data=user_information, columns=column_name)
# Saving DataFrame to CSV file
problem_df.to_csv("./gachon_algorithm_stats.csv", index=False)
