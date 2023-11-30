import time
import pandas as pd

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


driver_option = webdriver.ChromeOptions()
driver_option.add_argument('headless')

driver = webdriver.Chrome(options=driver_option) 
driver.implicitly_wait(3)

try:
    MAX_PAGE = 299
    problem_information = []

    for page in tqdm(range(MAX_PAGE)):
        driver.get(f'https://www.acmicpc.net/problemset/{page + 1}')
        time.sleep(3)

        # 문제 정보 가져오기
        problemIds       = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']")
        problemNames     = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[1]")
        solveCounts      = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[3]/a")
        submissionCounts = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[4]/a")
        correctRatios    = driver.find_elements(by=By.XPATH, value="//td[@class='list_problem_id']/following-sibling::td[5]")

        list_len = {len(lst) for lst in [problemIds, problemNames, solveCounts, submissionCounts, correctRatios]}
        if len(list_len) != 1:
            print (f"[ERROR] It might have an error with page #{page}")

        for e1, e2, e3, e4, e5 in zip(problemIds, problemNames, solveCounts, submissionCounts, correctRatios):
            problem_information.append([e1.text, "\"" + e2.text + "\"", e3.text, e4.text, (e5.text)[:-1]])

finally:
    driver.quit()


column_name = ['problemId', 'problemTitle', 'solved', 'submissionCount', 'correctRatio']
problem_df = pd.DataFrame(data=problem_information, columns=column_name)
problem_df.to_csv("./problem_info_data.csv", index=False)
