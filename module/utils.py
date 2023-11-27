import pandas as pd


problem_info_df = pd.read_csv("./data/filtered_problem_information.csv")
user_tier_df = pd.read_csv("./data/gachon_user_tier.csv")

column_map = {
    "problemId": "문제번호",
    "problemTitle": "문제이름",
    "solved": "맞힌사람",
    "submissionCount": "제출횟수",
    "correcRatio": "정답비율",
    "difficulty": "난이도"
}

difficulty_dict = {
    0: ("Unrated", "#2D2D2D"),
    1: ("Bronze V", "#9D4900"),
    2: ("Bronze IV", "#A54F00"),
    3: ("Bronze III", "#AD5600"),
    4: ("Bronze II", "#B55D0A"),
    5: ("Bronze I", "#C67739"),
    6: ("Silver V", "#38546E"),
    7: ("Silver IV", "#3D5A74"),
    8: ("Silver III", "#435F7A"),
    9: ("Silver II", "#496580"),
    10: ("Silver I", "#4E6A86"),
    11: ("Gold V", "#D28500"),
    12: ("Gold IV", "#DF8F00"),
    13: ("Gold III", "#EC9A00"),
    14: ("Gold II", "#F9A518"),
    15: ("Gold I", "#FFB028"),
    16: ("Platinum V", "#00C78B"),
    17: ("Platinum IV", "#00D497"),
    18: ("Platinum III", "#27E2A4"),
    19: ("Platinum II", "#3EF0B1"),
    20: ("Platinum I", "#51FDBD"),
    21: ("Diamond V", "#009EE5"),
    22: ("Diamond IV", "#00A9F0"),
    23: ("Diamond III", "#00B4FC"),
    24: ("Diamond II", "#2BBFFF"),
    25: ("Diamond I", "#41CAFF"),
    26: ("Ruby V", "#E0004C"),
    27: ("Ruby IV", "#EA0053"),
    28: ("Ruby III", "#F5005A"),
    29: ("Ruby II", "#FF0062"),
    30: ("Ruby I", "#FF3071"),
}


def get_problem_information(recommended_list: list):
    df = problem_info_df[problem_info_df['problemId'].isin(recommended_list)]
    df = df.rename(columns=column_map)
    df = df.reset_index(drop=True)

    return df


def get_user_tier(user_list: list):
    colors = []
    for user, _ in user_list:
        tier = user_tier_df.loc[user_tier_df['user_id'] == user, 'tier'].item()
        colors.append(difficulty_dict[tier])

    return colors