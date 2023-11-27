import pickle
import random
import pandas as pd
from matrix_factorization import KernelMF
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, mean_squared_error

# Constants for file paths
PICKLE_SAVE_PATH = "./asset/matrix_factorization.pickle"
FILTERED_PROBLEM_PATH = "./data/filtered_problem_information.csv"
FILTERED_USER_SOLVED_PROBLEM_PATH = "./data/filtered_gachon_userinformation.csv"
USER_TIER_PATH = "./data/gachon_user_tier.csv"

# Dictionary to map user tiers to numerical values
tier_partition = {
    0.0: 3, 0.1: 2, 0.2: 1, 0.3: 0, 0.4: -1, 0.5: -2,
    0.6: -3, 0.7: -4, 0.8: -5, 0.9: -7, 1.0: -8,
}


def train(epoch=100, factor=300, lr=0.01):
    """
    Train a matrix factorization model to predict user-item (problem) interactions.
    
    Parameters:
    epoch (int): Number of training epochs.
    factor (int): Number of latent factors.
    lr (float): Learning rate for training.
    """
    
    # Load dataset with negative samples
    rating_data = pd.read_csv("./data/merged_gachon_userinformation.csv")

    # Extract unique user and item (problem) IDs
    users = rating_data['user_id'].unique()
    items = rating_data['item_id'].unique()

    # Create mappings for user and item IDs
    user_to_index = {user: idx for idx, user in enumerate(users)}
    item_to_index = {item: idx for idx, item in enumerate(items)}
    index_to_item = {idx: item for idx, item in enumerate(items)}

    # Apply mappings to dataset
    rating_data['user_id'] = rating_data['user_id'].apply(lambda user: user_to_index[user])
    rating_data['item_id'] = rating_data['item_id'].apply(lambda item: item_to_index[item])

    # Split dataset into training and testing sets
    train_data, test_data = train_test_split(rating_data, test_size=0.2, random_state=42)
    train_X, train_y = train_data[['user_id', 'item_id']], train_data['rating']
    test_X, test_y = test_data[['user_id', 'item_id']], test_data['rating']

    # Initialize and train the model
    mf_model = KernelMF(n_epochs=epoch, n_factors=factor, verbose=False, lr=lr, reg=0.005)
    mf_model.fit(train_X, train_y)

    # Evaluate the model
    predictions = mf_model.predict(test_X)
    logloss = log_loss(test_y, predictions)
    rmse = mean_squared_error(test_y, predictions, squared=False)
    print(f"Log Loss: {logloss}, RMSE: {rmse}")

    # Save the trained model
    with open(PICKLE_SAVE_PATH, 'wb') as file:
        pickle.dump(mf_model, file)

    # Save mapping information
    with open("./asset/mapping.pickle", 'wb') as file:
        pickle.dump([user_to_index, item_to_index, index_to_item], file)


def predict(user_id: str, threshold: float):
    """
    Predict problems for a user based on their tier and a threshold.
    
    Parameters:
    user_id (str): The user's ID.
    threshold (float): The threshold for selecting problems.
    
    Returns:
    list: A list of recommended problem IDs.
    """
    
    # Load the trained model and mapping information
    with open(PICKLE_SAVE_PATH, "rb") as file:
        model = pickle.load(file)
    with open("./asset/mapping.pickle", "rb") as file:
        user_to_index, item_to_index, index_to_item = pickle.load(file)

    # Get user's tier
    user_tier_data = pd.read_csv(USER_TIER_PATH)
    user_tier = user_tier_data.loc[user_tier_data["user_id"] == user_id, "tier"].item()
    print(f"[DEBUG] Tier of user {user_id}: {user_tier}")

    # Define problem tier range based on threshold
    min_tier = max(user_tier + tier_partition[round(threshold, 2)], 0)
    max_tier = min(min_tier + 20, 30)
    print(f"[DEBUG] Recommended problem difficulty range for threshold {threshold}: {min_tier}, {max_tier}")

    # Load problem information and apply item ID mapping
    problem_data = pd.read_csv(FILTERED_PROBLEM_PATH)
    problem_data["problemId"] = problem_data["problemId"].apply(lambda x: item_to_index.get(x, -1))
    problems = problem_data["problemId"].tolist()

    # Identify problems not yet solved by the user
    user_solved_data = pd.read_csv(FILTERED_USER_SOLVED_PROBLEM_PATH)
    user_solved_data['problemId'] = user_solved_data['problemId'].apply(lambda x: item_to_index.get(x, -1))
    solved_problems = set(user_solved_data[user_solved_data["userName"] == user_to_index.get(user_id, -1)]["problemId"])
    unsolved_problems = [problem for problem in problems if problem not in solved_problems]

    # Predict ratings for unsolved problems within the difficulty range
    unsolved_problems_data = pd.DataFrame(unsolved_problems, columns=["problemId"])
    unsolved_problems_data = pd.merge(unsolved_problems_data, problem_data[['problemId', 'difficulty']], on='problemId')
    unsolved_problems_data = unsolved_problems_data.rename(columns={"problemId": "item_id"})
    unsolved_problems_data["user_id"] = user_to_index.get(user_id, -1)
    unsolved_problems_data["predicted_rating"] = model.predict(unsolved_problems_data)
    filtered_problems = unsolved_problems_data[(unsolved_problems_data['difficulty'] >= min_tier) & (unsolved_problems_data['difficulty'] <= max_tier)]

    print(filtered_problems.head())
    # Select problems based on threshold
    recommended_problems = [
        index_to_item[problem]
        for _, (problem, _, _, predicted_rating) in filtered_problems.iterrows()
        if round(predicted_rating, 2) == threshold
    ]

    # Shuffle and return the top 5 recommended problems
    random.shuffle(recommended_problems)
    return recommended_problems[:5]
