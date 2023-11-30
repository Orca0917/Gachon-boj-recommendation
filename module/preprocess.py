import random
import pandas as pd
from tqdm import tqdm
from collections import Counter


# Constants for file paths
PROBLEM_INFO_DATA           = "../data/problem_info_data.csv"
PROBLEM_TIER_DATA           = "../data/problem_tier_data.csv"
PROBLEM_DATA                = "../data/problem_data.csv"

PREPROCESSED_PROBLEM_DATA   = "../data/preprocessed_problem_data.csv"

USER_DATA                   = "../data/gachon_user_data.csv"
PREPROCESSED_USER_DATA      = "../data/preprocessed_gachon_user_data.csv"

NEGATIVE_SAMPLED_USER_DATA  = "../data/negative_sampled_user_data.csv"  # positive + negative samples


def mege_problem_information():
    problem_info_df = pd.read_csv(PROBLEM_INFO_DATA)
    probelm_tier_df = pd.read_csv(PROBLEM_TIER_DATA)

    problem_df = problem_info_df.merge(probelm_tier_df, on='problemId', how='left')
    problem_df = problem_df.sort_values(by='problemId')
    problem_df['tier'] = problem_df['tier'].fillna(0)

    problem_df.to_csv(PROBLEM_DATA, index=False)


def filter_problems(threshold):
    """
    Filter problems based on the number of times they have been solved.
    
    Parameters:
    threshold (int): The minimum number of times a problem should be solved to be included.
    """
    
    # Load problem data and apply filter
    problem_df = pd.read_csv(PROBLEM_DATA)
    filtered_data = problem_df[problem_df['solved'] >= threshold]
    filtered_data.to_csv(PREPROCESSED_PROBLEM_DATA, index=False)
    
    # Display stats about the filtered problems
    difficulty_counts = Counter(filtered_data['difficulty'].values)
    print("- Total number of problems:", sum(difficulty_counts.values()))
    print(sorted(difficulty_counts.items()))


def filter_user_solved_problems():
    """
    Filter user-solved problems based on the filtered problems list.
    사용자가 문제를 푼 목록 중, 문제가 threshold회 이상 풀린것들만 남기기
    """
    
    preprocessed_problem_df = pd.read_csv(PREPROCESSED_PROBLEM_DATA)
    user_df = pd.read_csv(USER_DATA)
    
    # Convert problem IDs to integers
    filtered_problems = [int(problem) for problem in preprocessed_problem_df['problemId'].tolist()]
    preprocessed_user_data = []

    # Filter user solved problems
    for _, (user_name, problem_id, user_tier) in tqdm(user_df.iterrows(), total=len(user_df)):
        if int(problem_id) in filtered_problems:
            preprocessed_user_data.append([user_name, int(problem_id), int(user_tier)])
        
    # Save the filtered data
    preprocessed_user_df = pd.DataFrame(data=preprocessed_user_data, columns=["userName", "problemId". "userTier"])
    preprocessed_user_df.to_csv(PREPROCESSED_USER_DATA, index=False)


def perform_negative_sampling(negative_proportion=0.5):
    """
    Perform negative sampling for the user-problem interactions.
    
    Parameters:
    negative_proportion (float): Proportion of negative samples relative to positive samples.
    """
    
    preprocessed_user_df = pd.read_csv(PREPROCESSED_USER_DATA)
    preprocessed_user_df = preprocessed_user_df.rename(columns={'userName': 'user_id', 'problemId': 'item_id'})
    preprocessed_user_df['rating'] = 1  # Assigning a positive rating

    problem_info = pd.read_csv(PREPROCESSED_PROBLEM_DATA)
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

    # Create DataFrame for negative samples and merge with positive samples
    negative_sample_df = pd.DataFrame(negative_samples, columns=["user_id", "item_id"])
    negative_sample_df['rating'] = 0

    merged_data = pd.concat([preprocessed_user_df, negative_sample_df], ignore_index=True)
    merged_data.to_csv(NEGATIVE_SAMPLED_USER_DATA, index=False)


if __name__ == "__main__":
    mege_problem_information()
    filter_problems(threshold=100)
    filter_user_solved_problems()
    perform_negative_sampling(negative_proportion=1.0)
