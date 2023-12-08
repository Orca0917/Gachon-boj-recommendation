import pandas as pd
from config import Config

cfg = Config()

# Counters for different types of requests (seemingly for tracking)
cnt_visit = 0
cnt_req_mf = 0
cnt_req_ubcf = 0
cnt_req_cbcf = 0

# Loading preprocessed problem data and user tier data from the configuration
problem_info_df = pd.read_csv(cfg.PREPROCESSED_PROBLEM_DATA[0])
user_tier_df = pd.read_csv(cfg.GACHON_USER_TIER_DATA[0])

# Mapping column names from English to Korean
column_map = {
    "problemId": "문제번호",
    "problemTitle": "문제이름",
    "solved": "맞힌사람",
    "submissionCount": "제출횟수",
    "correcRatio": "정답비율",
    "difficulty": "난이도"
}

# Dictionary mapping difficulty levels to tier names and color codes
difficulty_dict = {
    # Mapping from difficulty level to (Tier Name, Color Code)
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
    """
    Retrieves information for a list of recommended problems.
    
    Parameters:
    recommended_list (list): A list of problem IDs for which information is to be retrieved.
    
    Returns:
    DataFrame: A DataFrame containing information about the recommended problems.
    """
    # Filter the dataframe to include only the recommended problems
    df = problem_info_df[problem_info_df['problemId'].isin(recommended_list)]
    
    # Rename columns based on the predefined mapping
    df = df.rename(columns=column_map)
    
    # Reset index of the DataFrame
    df = df.reset_index(drop=True)

    return df

def get_user_tier(user_list: list):
    """
    Retrieves the tier and color code for a list of users.
    
    Parameters:
    user_list (list): A list of tuples containing user IDs and additional data.
    
    Returns:
    list: A list of tuples with each tuple containing the tier and color code for a user.
    """
    colors = []
    for user, _ in user_list:
        # Find the user's tier based on their user ID
        tier = user_tier_df.loc[user_tier_df['user_id'] == user, 'tier'].item()
        
        # Append the corresponding color code to the list
        colors.append(difficulty_dict[tier])

    return colors
