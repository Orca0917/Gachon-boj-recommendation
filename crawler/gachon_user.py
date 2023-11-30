"""
가천대학교의 유저 정보를 크롤링

백준 온라인 저지에 존재하는 가천대학교 학생들을 대상으로
현재 풀이한 문제들의 목록을 파악 + 유저의 티어정보도 파악
"""

import time
import pandas as pd

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

try:
    # 크롬드라이버 옵션 (창 안보이게 숨기기)
    driver_option = webdriver.ChromeOptions()
    driver_option.add_argument('headless')

    # 크롬드라이버 실행
    driver = webdriver.Chrome(options=driver_option) 
    driver.implicitly_wait(3)

    # 클롤링 된 정보가 저장
    user_data = []

    driver.get('https://www.acmicpc.net/school/ranklist/187')
    time.sleep(3)

    page_elem = driver.find_elements(by=By.XPATH, value="(//ul[@class='pagination']/li/a)[position()>1]")
    MAX_PAGE = max([int(elem.get_attribute('href').split("/")[-1]) for elem in page_elem])


    for page in tqdm(range(MAX_PAGE)):
        driver.get(f'https://www.acmicpc.net/school/ranklist/187/{page + 1}')
        time.sleep(3)

        gachon_user_elem = driver.find_elements(by=By.CSS_SELECTOR, value='#ranklist > tbody > tr > td:nth-child(2) > a')
        user_list = [user_elem.get_attribute('href').split("/")[-1] for user_elem in gachon_user_elem] # 현재 page의 가천대학교 학생 목록

        pbar = tqdm(user_list, leave=False)
        for user_name in pbar:
            driver.get(f'https://www.acmicpc.net/user/{user_name}')  # 백준 유저 정보 페이지 접속
            
            # (1) 유저의 티어정보가 보일때 까지 wait
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//*[@class='page-header']/h1"))
            )

            # (2) 유저의 문제풀이 이력이 보일 때 까지 wait
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'panel') and contains(@class, 'panel-default') and .//h3[contains(text(), '맞은 문제')]]//a"))
            )

            # -- 유저의 티어 정보
            user_tier = None
            try:
                solvedac_tier_img_tag = driver.find_element(by=By.XPATH, value="//*[@class='page-header']/h1/a/img")
                solvedac_tier_tag_src = solvedac_tier_img_tag.get_attribute('src').split("/")[-1]
                solvedac_tier_num = int(solvedac_tier_tag_src.split(".")[0])
                pbar.set_postfix(name=user_name, tier=solvedac_tier_num, refresh=True)
                user_tier = 0 if solvedac_tier_num == -1 else solvedac_tier_num
            except:
                user_tier = 0
                
            # -- 유저가 해결한 문제
            solved_problems = driver.find_elements(by=By.XPATH, value="//div[contains(@class, 'panel') and contains(@class, 'panel-default') and .//h3[contains(text(), '맞은 문제')]]//a")
            for solved in solved_problems:
                user_data.append([user_name, solved.text, user_tier])

finally:
    driver.quit()

# -- csv 파일로 저장
column_name = ['userName', 'problemId', 'userTier']
gachon_user_df = pd.DataFrame(data=user_data, columns=column_name)
gachon_user_df.to_csv("./gachon_user_data.csv", index=False)