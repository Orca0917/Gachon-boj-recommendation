import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By

# Setting up Chrome driver options for headless mode
driver_option = webdriver.ChromeOptions()
driver_option.add_argument('headless')

# Initializing Chrome driver
driver = webdriver.Chrome(options=driver_option) 
driver.implicitly_wait(3)  # Implicit wait for elements to load

try:
    # Total number of pages to scrape
    MAX_PAGE = 299
    # List to store problem information
    problem_information = []

    # Looping through each page
    for page in tqdm(range(MAX_PAGE)):
        # Accessing the problem set page
        driver.get(f'https://www.acmicpc.net/problemset/{page + 1}')
        time.sleep(3)  # Delay for page load

        # Fetching problem details
        problemIds = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']")
        problemNames = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[1]")
        solveCounts = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[3]/a")
        submissionCounts = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[4]/a")
        correctRatios = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[5]")

        # Checking for consistency in data length
        list_len = {len(lst) for lst in [problemIds, problemNames, solveCounts, submissionCounts, correctRatios]}
        if len(list_len) != 1:
            print(f"[ERROR] There might be an error with page #{page}")

        # Compiling problem data
        for e1, e2, e3, e4, e5 in zip(problemIds, problemNames, solveCounts, submissionCounts, correctRatios):
            problem_information.append([e1.text, "\"" + e2.text + "\"", e3.text, e4.text, (e5.text)[:-1]])

finally:
    # Closing the driver after scraping
    driver.quit()

# Defining column names and creating a DataFrame
column_name = ['problemId', 'problemTitle', 'solved', 'submissionCount', 'correctRatio']
problem_df = pd.DataFrame(data=problem_information, columns=column_name)
# Saving the DataFrame to a CSV file
problem_df.to_csv("./problem_info_data.csv", index=False)
