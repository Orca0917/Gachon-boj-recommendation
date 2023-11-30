import time
import pandas as pd

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


try:
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)

    MAX_LEVEL = 30
    problem_tier_data, level_failed, page_failed = [], [], []

    for level in tqdm(range(MAX_LEVEL), desc='LEVEL crawling'):
        driver.get(f'https://solved.ac/problems/level/{level + 1}')
        time.sleep(3)

        # 문제 정보 가져오기
        page_elem = driver.find_elements(by=By.CSS_SELECTOR, value='.css-18lc7iz > a')
        if len(page_elem) == 0:
            level_failed.append(f"level-{level}")
        MAX_PAGE = max([int(elem.get_attribute('href').split("=")[-1]) for elem in page_elem])

        for page in tqdm(range(MAX_PAGE), desc='Page crawling', leave=False):
            driver.get(f'https://solved.ac/problems/level/{level + 1}?page={page + 1}')
            time.sleep(3)

            # 문제 정보 가져오기
            problem_elem = driver.find_elements(by=By.CSS_SELECTOR, value='.css-lywkv4 > span > a')
            if len(problem_elem) == 0:
                page_failed.append(f"level-{level}-page-{page}")

            for elem in problem_elem:
                problem_tier_data.append([int(elem.get_attribute('href').split("/")[-1]), level])

finally:
    driver.quit()

column_name = ['problemId', 'tier']
pd.DataFrame(data=problem_tier_data, columns=column_name).to_csv("./problem_tier_data.csv", index=False)
