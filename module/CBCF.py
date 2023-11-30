import random
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from config import Config

cfg = Config()

def predict(user_id: str, num_similar_users: int):
    """
    Recommend new programming problems for a user, find similar users, and their similarity scores.

    Parameters:
    user_id (str): The ID of the user for whom to recommend problems and find similar users.
    num_similar_users (int): The number of similar users to consider.

    Returns:
    tuple: A tuple containing a list of recommended problem IDs, a list of similar user IDs, and their similarity scores.
    """

    # Load datasets
    solvedac_data   = pd.read_csv(cfg.GACHON_ALGORITHM_STATUS[0])
    gachon_data     = pd.read_csv(cfg.PREPROCESSED_GACHON_USER_DATA[0])

    # Calculate cosine similarity between users
    user_tags = solvedac_data.iloc[:, 1:]
    cosine_similarity_matrix = cosine_similarity(user_tags)
    similarity_df = pd.DataFrame(cosine_similarity_matrix, index=solvedac_data['userName'], columns=solvedac_data['userName'])

    # Find Top N Similar Users and their similarity scores
    similar_users_scores = similarity_df[user_id].sort_values(ascending=False)[1:num_similar_users+1]
    similar_users = similar_users_scores.index.tolist()
    similarity_scores = similar_users_scores.tolist()

    # Aggregate Problems Solved by Similar Users
    similar_users_problems = gachon_data[gachon_data['userName'].isin(similar_users)]

    # Filter Out Problems Already Solved by the Selected User
    solved_problems = gachon_data[gachon_data['userName'] == user_id]['problemId'].tolist()
    recommended_problems = similar_users_problems[~similar_users_problems['problemId'].isin(solved_problems)]

    # Recommend New Problems
    unique_recommended_problems = recommended_problems['problemId'].unique()

    # Randomly shuffle and limit the number of recommended problems
    random.shuffle(unique_recommended_problems)
    recommended_problems_list = unique_recommended_problems[:5] if len(unique_recommended_problems) > 5 else unique_recommended_problems

    # Return recommended problems, similar users, and their similarity scores
    return recommended_problems_list, list(zip(similar_users, similarity_scores))
