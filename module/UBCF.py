import random
import pickle
import numpy as np
import pandas as pd
from config import Config
from sklearn.metrics.pairwise import cosine_similarity

N_PROBLEM = 10000  # Total number of problems

cfg = Config()

def train():
    """
    Train a user-item interaction matrix based on the problem-solving history of users.
    """
    
    # Load dataset containing problem-solving records
    user_data = pd.read_csv(cfg.PREPROCESSED_USER_DATA[0])

    # Load user and item mappings from a file
    with open(cfg.ASSET_MAPPING[0], "rb") as file:
        user_to_index, item_to_index, index_to_item = pickle.load(file)

    # Extract unique users and count them
    users = user_data['userName'].unique()
    num_users = len(users)

    # Initialize a matrix to represent user-item interactions
    user_item_matrix = np.zeros((num_users, N_PROBLEM))

    # Populate the matrix with user-item interactions
    for _, row in user_data.iterrows():
        user_idx = user_to_index[row['userName']]
        problem_idx = item_to_index[row['problemId']]
        user_item_matrix[user_idx, problem_idx] = 1

    # Save the user-item interaction matrix for later use
    with open(cfg.ASEST_UBCF[0], 'wb') as file:
        pickle.dump(user_item_matrix, file)

def predict(user_id: str, threshold: int):
    """
    Predict problems for a given user based on similarity to other users and return the most similar users.
    
    Parameters:
    user_id (str): ID of the user.
    threshold (int): Number of similar users to consider for recommendations.

    Returns:
    tuple: Contains a list of recommended problem IDs, similar user IDs, and similarity scores.
    """
    
    # Load the user-item interaction matrix and mappings
    with open(cfg.ASEST_UBCF[0], 'rb') as file:
        user_item_matrix = pickle.load(file)
    with open(cfg.ASSET_MAPPING[0], "rb") as file:
        user_to_index, item_to_index, index_to_item = pickle.load(file)

    # Reverse mapping for indices to users
    index_to_user = {v: k for k, v in user_to_index.items()}

    # Get the problems solved by the user
    user_data = pd.read_csv(cfg.PREPROCESSED_GACHON_USER_DATA[0])
    solved_problems = user_data[user_data['userName'] == user_id]['problemId'].tolist()

    # Create a new user interaction vector
    new_user_interaction = np.zeros(N_PROBLEM)
    for problem in solved_problems:
        new_user_interaction[item_to_index[problem]] = 1
    
    # Add new user data to the existing matrix
    user_item_matrix = np.vstack([user_item_matrix, new_user_interaction])

    # Compute cosine similarity between users
    cosine_sim = cosine_similarity(user_item_matrix)
    new_user_similarity = cosine_sim[-1][:-1]

    # Find the most similar users and their similarity scores
    top_similar_users_indices = np.argsort(new_user_similarity)[::-1][1: 1 + threshold]
    similar_users_and_scores = [(index_to_user[idx], new_user_similarity[idx]) for idx in top_similar_users_indices]

    # Generate recommendations based on similar users' problem-solving patterns
    recommended_problems = set()
    for user_idx in top_similar_users_indices:
        solved_by_user = np.where(user_item_matrix[user_idx] == 1)[0]
        recommended_problems.update(set(solved_by_user) - set(solved_problems))

    # Convert problem indices back to IDs and shuffle
    recommended_problems = [index_to_item[problem] for problem in recommended_problems]
    random.shuffle(recommended_problems)

    # Return top 5 recommendations and similar users with their scores
    return recommended_problems[:5], similar_users_and_scores
