import requests
import json
import pytz
import pandas as pd
import streamlit as st
from datetime import datetime
from module import MF, UBCF, CBCF, utils
from config import Config
cfg = Config()
<<<<<<< HEAD



# Preparing the dataset
aws_apigateway_url = "https://evkdmpdtql.execute-api.ap-northeast-2.amazonaws.com/gachonboj-stage/gachonboj-{}"
solvedac_gachon_user = pd.read_csv(cfg.GACHON_ALGORITHM_STATUS[0])["userName"].unique()
boj_gachon_user = pd.read_csv(cfg.GACHON_USER_DATA[0])["userName"].unique()
=======



# -- preparing dataset
solvedac_gachon_user = pd.read_csv(cfg.GACHON_ALGORITHM_STATUS[0])[
    "userName"
].unique()
boj_gachon_user = pd.read_csv(cfg.GACHON_USER_DATA[0])[
    "userName"
].unique()
>>>>>>> 6aab76bf53d15124a3fb8947954e7544c71c7f81
sim_users = None

# Define a callback function for when the algorithm selection changes
def on_algorithm_change():
    # Reset session state if the selected algorithm changes
    if "selected_algorithm" in st.session_state and st.session_state["selected_algorithm"] != st.session_state["algorithm_select"]:
        st.session_state["user_id"] = None
        st.session_state["algorithm"] = None

    # Store the currently selected algorithm
    st.session_state["selected_algorithm"] = st.session_state["algorithm_select"]

# Sidebar for selecting the recommendation algorithm
algorithm = st.sidebar.selectbox(
    "Select the algorithm to be used for problem recommendation",
    [
        "Matrix Factorization",
        "User Based Collaborative Filtering",
        "Content Based Collaborative Filtering",
    ],
    on_change=on_algorithm_change,
    key="algorithm_select",
)

st.markdown(
    """
    <style>
    a:link {
        color: inherit;  /* 기본 텍스트 색상으로 설정 */
    }
    a:visited {
        color: inherit;
    }
    a:hover {
        color: #644fff;
    }
    a:active {
        color: inherit;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    """
    ---
    ### 1️⃣ Matrix Factorization
    해당 알고리즘은 각 사용자에게 맞춤형 문제를 추천할 수 있게 되며, 사용자가 아직 시도하지 않았지만 관심을 가질 만한 새로운 문제들을 제안하는 데 활용됩니다. 
    """
)
st.sidebar.markdown(
    """
    ### 2️⃣ User Based Collaborative Filtering
    한 사용자가 풀었지만 다른 유사한 사용자가 아직 풀지 않은 문제를 추천함으로써, 개별 사용자에게 관련성이 높은 맞춤형 문제를 제공합니다.
    """
)

st.sidebar.markdown(
    """
    ### 3️⃣ Content Based Collaborative Filtering
    각 문제의 내용과 특성(난이도, 태그, 정답률 등)을 분석하여 사용자의 과거 활동과 선호도와 매칭하여 보다 정확하고 맞춤화된 문제 추천을 가능하게 합니다.
    """
)

st.sidebar.markdown(
    """
    ---
    <img src="https://github.com/Orca0917/Orca0917.github.io/assets/91870042/b7796ace-9bef-4007-b451-5813a913d02f" width="32" height="28"> [Baekjoon Online Judge](https://www.acmicpc.net)  
    <img src="https://static.solved.ac/logo.svg" width="32" height="32"> [Solved.ac](https://solved.ac/)
    """,
    unsafe_allow_html=True,
)

# Adding title and description
st.title("가천대학교 백준 문제 추천 서비스")

# Description of the website
st.markdown(
    """
    ### 👋 안녕하세요  
    이 웹사이트는 가천대학교 학생들이 [Baekjoon Online Judge](https://noj.am) 에서 어떤 문제를 풀어야 할지 결정하는 데 도움을 주기 위해 개발되었습니다.
    아직은 프로토타입 단계이므로, 사용해보시고 다양한 피드백을 주시면 감사하겠습니다. 🙇🏻‍♂️
    """
)

st.write("\n" * 5)

st.markdown(
    f"""
    ### 🤠 사용법  
    왼쪽 사이드바에서 여러 가지 문제 추천 알고리즘 중 하나를 선택할 수 있습니다. 현재 선택된 알고리즘은 <span style='color: #644fff;'>'{st.session_state["algorithm_select"]}'</span> 입니다.
    아래에 있는 텍스트 입력창에 본인의 백준 아이디를 입력하시면, 선택하신 알고리즘에 따라 맞춤형 문제 추천을 받으실 수 있습니다.
    """,
    unsafe_allow_html=True
)

st.write("\n" * 5)

# User ID input
user_id = st.text_input(
    "나의 백준아이디 입력하기",
    help="백준에서 사용되는 아이디를 입력하는 공간입니다. Gachon-student-001와 같은 아이디를 사용할 수 있습니다.",
    placeholder="Gachon-student-001",
)

# Button for getting recommendations
if st.button("문제 추천받기"):
    # Check if the user ID is in the list of known users
    if user_id not in boj_gachon_user:
        st.error(f"{user_id} 님을 가천대학교 재학생 목록 중 찾아보려고 했지만, 찾지 못했습니다😢 아직 재학생 목록에 반영되어 있지 않을 수 있으므로 내일 다시 시도해보시기 바랍니다.")
        st.session_state["algorithm"] = None
        st.session_state["user_id"] = None
    else:
        st.session_state["algorithm"] = algorithm
        st.session_state["user_id"] = user_id


# Slider for adjusting recommendation parameters and displaying recommended problems
if (
    "user_id" in st.session_state
    and "algorithm" in st.session_state
    and st.session_state["user_id"] is not None
):
    selected_algorithm = st.session_state["algorithm"]
    user_id = st.session_state["user_id"]

    st.markdown(
        f"""
        ---
        {user_id} 님을 위해 딱 맞는 문제를 준비해볼게요! 쉽게 풀 수 있는 문제부터 깊이 고민해볼 만한 도전적인 문제까지, 다양한 난이도의 문제를 선정해드릴게요.  
        """
    )

    # 알고리즘에 따른 추천 결과 표시
    if selected_algorithm == "Matrix Factorization":
        threshold = st.slider(
            f"하단 스크롤바를 조절하여 {user_id} 님이 문제를 맞출 확률을 조절할 수 있습니다.",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.1,
        )
        with st.spinner(f"{user_id} 님을 위한 문제를 준비중입니다 🏃🏻‍♂️"):
            utils.cnt_req_mf += 1
            json_data = json.dumps (
                {
                    "user_id": user_id,
                    "threshold": threshold
                }
            )
            response = requests.post(
                url=aws_apigateway_url.format("mf"),
                data=json_data,
                headers={
                    "Content-Type": "application/json"
                }
            )
            parsed_json = json.loads(response.text)
            body = json.loads(parsed_json['body'])
            recommended_problems = body['result']
            # recommended_problems = MF.predict(user_id=user_id, threshold=threshold)
        recommended_problems = utils.get_problem_information(recommended_problems)

    elif selected_algorithm == "User Based Collaborative Filtering":
        threshold = st.slider(
            f"하단 스크롤바를 조절하여 {user_id}님의 문제 추천에 반영할 유사한 학생의 수를 조절할 수 있습니다.",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
        )
        with st.spinner(f"{user_id} 님을 위한 문제를 준비중입니다 🏃🏻‍♂️"):
            utils.cnt_req_ubcf += 1
            json_data = json.dumps (
                {
                    "user_id": user_id,
                    "n_similar": threshold
                }
            )
            response = requests.post(
                url=aws_apigateway_url.format("ubcf"),
                data=json_data,
                headers={
                    "Content-Type": "application/json"
                }
            )
            parsed_json = json.loads(response.text)
            body = json.loads(parsed_json['body'])
            recommended_problems = body['result']
            sim_users = body['similarity']
            # recommended_problems, sim_users = UBCF.predict(user_id=user_id, threshold=threshold)
        recommended_problems = utils.get_problem_information(recommended_problems)

    elif selected_algorithm == "Content Based Collaborative Filtering":
        # 1. content based collaborative filtering 을 사용하기 위해서는 해당 사용자가 solved ac 가입자 이어야 한다.
        if user_id not in solvedac_gachon_user:
            st.error(
                f"Content Based Collaborative Filtering을 사용하기 위해서는 Solved.ac 에 가입된 사용자이어야 합니다. 😢"
            )
            st.session_state["algorithm"] = None
            st.session_state["user_id"] = None

        else:
            threshold = st.slider(
                f"하단 스크롤바를 조절하여 {user_id}님의 문제 추천에 반영할 유사한 학생의 수를 조절할 수 있습니다.",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
            )
            with st.spinner(f"{user_id} 님을 위한 문제를 준비중입니다 🏃🏻‍♂️"):
                utils.cnt_req_cbcf += 1
                json_data = json.dumps (
                    {
                        "user_id": user_id,
                        "n_similar": threshold
                    }
                )
                response = requests.post(
                    url=aws_apigateway_url.format("cbcf"),
                    data=json_data,
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                parsed_json = json.loads(response.text)
                body = json.loads(parsed_json['body'])
                recommended_problems = body['result']
                sim_users = body['similarity']
                # recommended_problems, sim_users = CBCF.predict(
                #     user_id=user_id, num_similar_users=threshold
                # )
            recommended_problems = utils.get_problem_information(recommended_problems)
            # 4. 너무 쉬운 문제는 제거하기 위해, minimum으로 해당 사용자의 티어 - 3 이하의 문제는 추천되지 않도록 한다,

    if st.session_state["algorithm"] is not None:
        st.markdown(
            """
            ### 🎯 추천 결과
            """
        )
        for _, (
            prob_num,
            prob_name,
            _,
            _,
            _,
            difficulty,
        ) in recommended_problems.iterrows():
            
            st.markdown(
                f"- 문제번호: {prob_num} / 문제이름: {prob_name} / 난이도: <span style='color: {utils.difficulty_dict[difficulty][1]};'>{utils.difficulty_dict[difficulty][0]}</span> / [{prob_num}번 바로 풀러가기👈](https://www.acmicpc.net/problem/{prob_num})",
                unsafe_allow_html=True,
            )

        if st.session_state["algorithm"] is not None and st.session_state["algorithm"] != "Matrix Factorization":
            st.markdown(
                """
                ---
                ### 👥 나와 비슷한 유저들
                """
            )

            tier_info = utils.get_user_tier(sim_users)
            for (user, sim), (tier_name, tier_color) in zip(sim_users, tier_info):
                st.markdown(
                    f"- 유저 ID: [{user}](https://www.acmicpc.net/user/{user}) / 유사도: {sim: .4f} / 티어: <span style='color: {tier_color};'>{tier_name}</span>",
                    unsafe_allow_html=True
                )


# Footer for copyright notice
st.markdown(
    """
    ---
    사용자 정보 및 재학생 정보는 매일 정오에 업데이트 됩니다.  
    버그 및 오류 제보: 0917jong@gachon.ac.kr  
    개발: 유종문, 장원준, 오명석, 최수미
    """,
    unsafe_allow_html=True,
)

utils.cnt_visit += 1

# Tracking and logging visits and requests
local_tz = pytz.timezone('Asia/Seoul')
local_time = datetime.now(local_tz)
formatted_time = local_time.strftime('%H:%M:%S')
print(f"[INFO #{formatted_time}] visit={utils.cnt_visit:<5}, mf={utils.cnt_req_mf:<5}, ubcf={utils.cnt_req_ubcf:<5}, cbcf={utils.cnt_req_cbcf:<5}")
