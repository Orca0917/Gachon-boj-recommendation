import pickle
import random
import pandas as pd
from config import Config
from matrix_factorization import KernelMF
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, mean_squared_error

# Mapping user tiers to numerical values for partitioning
tier_partition = {
    0.0: 3, 0.1: 2, 0.2: 1, 0.3: 0, 0.4: -1, 0.5: -2,
    0.6: -3, 0.7: -4, 0.8: -5, 0.9: -7, 1.0: -8,
}

cfg = Config()


def train(epoch=100, factor=300, lr=0.01):
    """
    Train a matrix factorization model to predict user-item (problem) interactions.

    Parameters:
    epoch (int): Number of epochs for training.
    factor (int): Number of latent factors in the model.
    lr (float): Learning rate for the training process.
    """

    # Load dataset with negative samples for training
    rating_data = pd.read_csv(cfg.NEGATIVE_SAMPLED_USER_DATA[0])

    # Extract unique users and items (problems)
    users = rating_data['user_id'].unique()
    items = rating_data['item_id'].unique()

    # Mapping user and item IDs to indices
    user_to_index = {user: idx for idx, user in enumerate(users)}
    item_to_index = {item: idx for idx, item in enumerate(items)}
    index_to_item = {idx: item for item, idx in item_to_index.items()}

    # Applying mappings to the dataset
    rating_data['user_id'] = rating_data['user_id'].apply(lambda user: user_to_index[user])
    rating_data['item_id'] = rating_data['item_id'].apply(lambda item: item_to_index[item])

    # Splitting data into training and test sets
    train_data, test_data = train_test_split(rating_data, test_size=0.2, random_state=42)
    train_X, train_y = train_data[['user_id', 'item_id']], train_data['rating']
    test_X, test_y = test_data[['user_id', 'item_id']], test_data['rating']

    # Initializing and training the Matrix Factorization model
    mf_model = KernelMF(n_epochs=epoch, n_factors=factor, lr=lr, reg=0.005, min_rating=0, max_rating=1, verbose=10)
    mf_model.fit(train_X, train_y)

    # Evaluating model performance
    predictions = mf_model.predict(test_X)
    logloss = log_loss(test_y, predictions)
    rmse = mean_squared_error(test_y, predictions, squared=False)
    print(f"- Log Loss: {logloss}, \n- RMSE: {rmse}")

    # Save the trained model and mapping data (commented out)
    with open(cfg.ASSET_MF[0], 'wb') as file:
        pickle.dump(mf_model, file)
    with open(cfg.ASSET_MAPPING[0], 'wb') as file:
        pickle.dump([user_to_index, item_to_index, index_to_item], file)


def predict(user_id: str, threshold: float):
    """
    Predict problems for a user based on their tier and a specified threshold.

    Parameters:
    user_id (str): User's ID.
    threshold (float): Threshold for selecting problems.

    Returns:
    list: List of recommended problem IDs.
    """
    
    # Load trained model and mapping data
    with open(cfg.ASSET_MF[0], "rb") as file:
        model = pickle.load(file)
    with open(cfg.ASSET_MAPPING[0], "rb") as file:
        user_to_index, item_to_index, index_to_item = pickle.load(file)

    # Retrieve the user's tier from the dataset
    user_tier_df = pd.read_csv(cfg.GACHON_USER_TIER_DATA[0])
    user_tier = user_tier_df.loc[user_tier_df["user_id"] == user_id, "tier"].item()

    # Define problem tier range based on user tier and threshold
    min_tier = max(user_tier + tier_partition[round(threshold, 2)], 0)
    max_tier = min(min_tier + 20, 30)

    # Load problem data and apply item ID mapping
    problem_data = pd.read_csv(cfg.PREPROCESSED_PROBLEM_DATA[0])
    problem_data["problemId"] = problem_data["problemId"].apply(lambda x: item_to_index.get(x, -1))
    problems = problem_data["problemId"].tolist()

    # Identify problems not yet solved by the user
    user_solved_data = pd.read_csv(cfg.PREPROCESSED_GACHON_USER_DATA[0])
    user_solved_data['problemId'] = user_solved_data['problemId'].apply(lambda x: item_to_index.get(x, -1))
    solved_problems = set(user_solved_data[user_solved_data["userName"] == user_to_index.get(user_id, -1)]["problemId"])
    unsolved_problems = [problem for problem in problems if problem not in solved_problems]

    # Predict ratings for unsolved problems within difficulty range
    unsolved_problems_data = pd.DataFrame(unsolved_problems, columns=["problemId"])
    unsolved_problems_data = pd.merge(unsolved_problems_data, problem_data[['problemId', 'difficulty']], on='problemId')
    unsolved_problems_data = unsolved_problems_data.rename(columns={"problemId": "item_id"})
    unsolved_problems_data["user_id"] = user_to_index.get(user_id, -1)
    unsolved_problems_data["predicted_rating"] = model.predict(unsolved_problems_data)
    filtered_problems = unsolved_problems_data[(unsolved_problems_data['difficulty'] >= min_tier) & (unsolved_problems_data['difficulty'] <= max_tier)]

    # Select problems based on threshold and shuffle them
    recommended_problems = [
        index_to_item[problem]
        for _, (problem, _, _, predicted_rating) in filtered_problems.iterrows()
        if round(predicted_rating, 2) == threshold
    ]
    random.shuffle(recommended_problems)
    
    # Return top 5 recommended problems
    return recommended_problems[:5]
