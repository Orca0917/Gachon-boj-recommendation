import random
import pandas as pd
from tqdm import tqdm
from config import Config
from collections import Counter

cfg = Config()


def mege_problem_information():
    """
    Merges problem information and problem tier data, then saves the combined data.
    """
    # Load problem information and tier data
    problem_info_df = pd.read_csv(cfg.PROBLEM_INFO_DATA[0])
    problem_tier_df = pd.read_csv(cfg.PROBLEM_TIER_DATA[0])

    # Merge the two dataframes on 'problemId' and sort by it
    problem_df = problem_info_df.merge(problem_tier_df, on='problemId', how='left')
    problem_df = problem_df.sort_values(by='problemId')

    # Fill missing tier values with 0
    problem_df['tier'] = problem_df['tier'].fillna(0)

    # Save the merged data to a file
    problem_df.to_csv(cfg.PROBLEM_DATA[0], index=False)


def filter_problems(threshold):
    """
    Filters problems based on the minimum number of times they have been solved.
    
    Parameters:
    threshold (int): Minimum number of times a problem should be solved to be included.
    """
    # Load the merged problem data
    problem_df = pd.read_csv(cfg.PROBLEM_DATA[0])

    # Apply the threshold filter
    filtered_data = problem_df[problem_df['solved'] >= threshold]

    # Save the filtered data
    filtered_data.to_csv(cfg.PREPROCESSED_PROBLEM_DATA[0], index=False)
    
    # Display statistics about the filtered problems
    difficulty_counts = Counter(filtered_data['difficulty'].values)
    print("- Total number of problems:", sum(difficulty_counts.values()))
    print(sorted(difficulty_counts.items()))


def filter_user_solved_problems():
    """
    Filters user-solved problems based on the list of filtered problems.
    """
    # Load preprocessed problem data and original user data
    preprocessed_problem_df = pd.read_csv(cfg.PREPROCESSED_PROBLEM_DATA[0])
    user_df = pd.read_csv(cfg.USER_DATA[0])

    # Convert problem IDs to integers for comparison
    filtered_problems = [int(problem) for problem in preprocessed_problem_df['problemId'].tolist()]
    preprocessed_user_data = []

    # Filter out solved problems not in the filtered problems list
    for _, (user_name, problem_id, user_tier) in tqdm(user_df.iterrows(), total=len(user_df)):
        if int(problem_id) in filtered_problems:
            preprocessed_user_data.append([user_name, int(problem_id), int(user_tier)])
    
    # Save the filtered user data
    preprocessed_user_df = pd.DataFrame(data=preprocessed_user_data, columns=["userName", "problemId", "userTier"])
    preprocessed_user_df.to_csv(cfg.PREPROCESSED_USER_DATA[0], index=False)


def perform_negative_sampling(negative_proportion=0.5):
    """
    Performs negative sampling for the user-problem interactions to balance the dataset.
    
    Parameters:
    negative_proportion (float): Proportion of negative samples compared to positive samples.
    """
    # Load preprocessed user data
    preprocessed_user_df = pd.read_csv(cfg.PREPROCESSED_USER_DATA[0])
    preprocessed_user_df = preprocessed_user_df.rename(columns={'userName': 'user_id', 'problemId': 'item_id'})
    preprocessed_user_df['rating'] = 1  # Assigning a positive rating to existing interactions

    # Load problem data
    problem_info = pd.read_csv(cfg.PREPROCESSED_PROBLEM_DATA[0])
    problems = problem_info["problemId"].tolist()
    users = preprocessed_user_df['user_id'].unique()

    negative_samples = []

    # Generate negative samples for each user
    for user in tqdm(users):
        solved_problems = preprocessed_user_df[preprocessed_user_df['user_id'] == user]['item_id'].tolist()
        unsolved_problems = [problem for problem in problems if problem not in solved_problems]
        random.shuffle(unsolved_problems)

        num_negative_samples = int(len(solved_problems) * negative_proportion)
        sampled_negatives = unsolved_problems[:num_negative_samples]
        negative_samples.extend([[user, problem] for problem in sampled_negatives])

    # Combine negative samples with positive samples and save
    negative_sample_df = pd.DataFrame(negative_samples, columns=["user_id", "item_id"])
    negative_sample_df['rating'] = 0  # Assigning a negative rating to these interactions

    merged_data = pd.concat([preprocessed_user_df, negative_sample_df], ignore_index=True)
    merged_data.to_csv(cfg.NEGATIVE_SAMPLED_USER_DATA[0], index=False)

if __name__ == "__main__":
    # Execute the defined functions to process the problem data
    mege_problem_information()
    filter_problems(threshold=100)
    filter_user_solved_problems()
    perform_negative_sampling(negative_proportion=1.0)
