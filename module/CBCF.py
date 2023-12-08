import random
import pandas as pd
from config import Config
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

    # Load datasets from specified configuration paths
    solvedac_data = pd.read_csv(cfg.GACHON_ALGORITHM_STATUS[0])
    gachon_data = pd.read_csv(cfg.PREPROCESSED_GACHON_USER_DATA[0])

    # Calculate cosine similarity between users based on their tags
    user_tags = solvedac_data.iloc[:, 1:]
    cosine_similarity_matrix = cosine_similarity(user_tags)
    similarity_df = pd.DataFrame(cosine_similarity_matrix, index=solvedac_data['userName'], columns=solvedac_data['userName'])

    # Find the top N similar users to the specified user and their similarity scores
    similar_users_scores = similarity_df[user_id].sort_values(ascending=False)[1:num_similar_users+1]
    similar_users = similar_users_scores.index.tolist()
    similarity_scores = similar_users_scores.tolist()

    # Aggregate problems solved by similar users
    similar_users_problems = gachon_data[gachon_data['userName'].isin(similar_users)]

    # Exclude problems already solved by the user
    solved_problems = gachon_data[gachon_data['userName'] == user_id]['problemId'].tolist()
    recommended_problems = similar_users_problems[~similar_users_problems['problemId'].isin(solved_problems)]

    # Select unique recommended problems
    unique_recommended_problems = recommended_problems['problemId'].unique()

    # Randomize and limit the number of recommended problems
    random.shuffle(unique_recommended_problems)
    recommended_problems_list = unique_recommended_problems[:5] if len(unique_recommended_problems) > 5 else unique_recommended_problems

    # Return a tuple of recommended problems, similar users, and their similarity scores
    return recommended_problems_list, list(zip(similar_users, similarity_scores))
