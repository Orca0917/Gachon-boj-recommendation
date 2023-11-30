import time
import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


MAX_PAGE = 7
user_information = []
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
    driver_option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)

    for page in tqdm(range(1, MAX_PAGE + 1)):
        driver.get(f'https://solved.ac/ranking/o/187?page={page}')
        time.sleep(3)

        # 유저 정보 가져오기
        userNames = driver.find_elements(by=By.XPATH, value="//tr[@class='css-1ojb0xa']/td[3]/span/a/b")
        userNames = [elem.text for elem in userNames]

        for idx, userName in enumerate(userNames):
            driver.get(f'https://solved.ac/profile/{userName}')
            time.sleep(3)
            status = []

            # -- 태그 더보기 확장
            while True:
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div[3]/div/div[8]/div[3]/div[3]"))
                    )
                    button = driver.find_element(By.XPATH, "//*[@id='__next']/div[3]/div/div[8]/div[3]/div[3]")
                    button.click()
                except TimeoutException:
                    print(f"[DEBUG] Page #{page}-{idx} 더 이상 더보기 버튼이 존재하지 않습니다.")
                    break

            # -- 태그 별 점수 불러오기
            for tag in tags:
                try:
                    stat = driver.find_element(by=By.XPATH, value=f"//a[contains(@href, '{tag}')]/../../../td[4]/b/span")
                    status.append(int(stat.text.split(" ")[-1]))
                except NoSuchElementException:
                    print(f"[DEBUG] 현재 유저 {userName}은 알고리즘 태그 #{tag}에 대한 풀이내역이 존재하지 않습니다")
                    status.append(0)

            user_information.append([userName] + status)
    
finally:
    driver.quit()

column_name = ['userName', 'tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8']
problem_df = pd.DataFrame(data=user_information, columns=column_name)
problem_df.to_csv("./gachon_algorithm_stats.csv", index=False)