import random
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from config import Config

N_PROBLEM = 10000  # Total number of problems

cfg = Config()

def train():
    """
    Train a user-item interaction matrix based on problem-solving history of users.
    """
    
    # Load dataset containing problem-solving records of students
    user_data = pd.read_csv(cfg.PREPROCESSED_USER_DATA[0])

    # Create mapping for user IDs to indices
    with open(cfg.ASSET_MAPPING[0], "rb") as file:
        user_to_index, item_to_index, index_to_item = pickle.load(file)

    # Extract unique users
    users = user_data['userName'].unique()
    num_users = len(users)

    # Initialize user-item matrix
    user_item_matrix = np.zeros((num_users, N_PROBLEM))

    # Populate the matrix based on data
    for _, row in user_data.iterrows():
        user_idx = user_to_index[row['userName']]
        problem_idx = item_to_index[row['problemId']]
        user_item_matrix[user_idx, problem_idx] = 1

    # Save the matrix for later use
    with open(cfg.ASEST_UBCF[0], 'wb') as file:
        pickle.dump(user_item_matrix, file)


def predict(user_id: str, threshold: int):
    """
    Predict problems for a given user based on similarity to other users, 
    and also return the most similar users and their similarity scores.
    
    Parameters:
    user_id (str): The ID of the user for whom to predict problems.
    threshold (int): The number of similar users to consider for recommendations.
    
    Returns:
    tuple: A tuple containing a list of recommended problem IDs, 
           a list of most similar user IDs, and their similarity scores.
    """
    
    # Load the user-item interaction matrix and mappings
    with open(cfg.ASEST_UBCF[0], 'rb') as file:
        user_item_matrix = pickle.load(file)
    with open(cfg.ASSET_MAPPING[0], "rb") as file:
        user_to_index, item_to_index, index_to_item = pickle.load(file)

    index_to_user = {v: k for k, v in user_to_index.items()}

    # Get problems solved by the user
    user_data = pd.read_csv(cfg.PREPROCESSED_GACHON_USER_DATA[0])
    solved_problems = user_data[user_data['userName'] == user_id]['problemId'].tolist()

    # Create a new user interaction vector
    new_user_interaction = np.zeros(N_PROBLEM)
    for problem in solved_problems:
        new_user_interaction[item_to_index[problem]] = 1
    
    # Add new user data to the matrix
    user_item_matrix = np.vstack([user_item_matrix, new_user_interaction])

    # Compute cosine similarity
    cosine_sim = cosine_similarity(user_item_matrix)
    new_user_similarity = cosine_sim[-1][:-1]

    # Find most similar users and their similarity scores
    top_similar_users_indices = np.argsort(new_user_similarity)[::-1][1: 1 + threshold]
    similar_users_and_scores = [(index_to_user[idx], new_user_similarity[idx]) for idx in top_similar_users_indices]

    # Generate recommendations
    recommended_problems = set()
    for user_idx in top_similar_users_indices:
        solved_by_user = np.where(user_item_matrix[user_idx] == 1)[0]
        recommended_problems.update(set(solved_by_user) - set(solved_problems))

    # Convert indices back to problem IDs and shuffle
    recommended_problems = [index_to_item[problem] for problem in recommended_problems]
    random.shuffle(recommended_problems)

    return recommended_problems[:5], similar_users_and_scores
