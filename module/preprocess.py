import pandas as pd
import random
from tqdm import tqdm
from collections import Counter

# Constants for file paths
PROBLEM_PATH = "../data/dataset_problem_information.csv"
FILTERED_PROBLEM_PATH = "../data/filtered_problem_information.csv"
USER_SOLVED_PROBLEM_PATH = "../data/dataset_gachon_userinformation.csv"
FILTERED_USER_SOLVED_PROBLEM_PATH = "../data/filtered_gachon_userinformation.csv"
MERGED_DATA_PATH = "../data/merged_gachon_userinformation.csv"  # positive + negative samples


def filter_problems(threshold):
    """
    Filter problems based on the number of times they have been solved.
    
    Parameters:
    threshold (int): The minimum number of times a problem should be solved to be included.
    """
    
    # Load problem data and apply filter
    problem_data = pd.read_csv(PROBLEM_PATH)
    filtered_data = problem_data[problem_data['solved'] >= threshold]
    filtered_data.to_csv(FILTERED_PROBLEM_PATH, index=False)
    
    # Display stats about the filtered problems
    difficulty_counts = Counter(filtered_data['difficulty'].values)
    print("- Total number of problems:", sum(difficulty_counts.values()))
    print(sorted(difficulty_counts.items()))


def filter_user_solved_problems():
    """
    Filter user-solved problems based on the filtered problems list.
    """
    
    filtered_problem_data = pd.read_csv(FILTERED_PROBLEM_PATH)
    user_problem_data = pd.read_csv(USER_SOLVED_PROBLEM_PATH)
    
    # Convert problem IDs to integers
    filtered_problems = [int(problem) for problem in filtered_problem_data['problemId'].tolist()]
    filtered_user_problems = []

    # Filter user solved problems
    for _, row in tqdm(user_problem_data.iterrows(), total=len(user_problem_data)):
        if int(row['problemId']) in filtered_problems and int(row['solved']) != 0:
            filtered_user_problems.append([row['userName'], int(row['problemId'])])
        
    # Save the filtered data
    filtered_user_problem_df = pd.DataFrame(data=filtered_user_problems, columns=["userName", "problemId"])
    filtered_user_problem_df.to_csv(FILTERED_USER_SOLVED_PROBLEM_PATH, index=False)


def perform_negative_sampling(negative_proportion=0.5):
    """
    Perform negative sampling for the user-problem interactions.
    
    Parameters:
    negative_proportion (float): Proportion of negative samples relative to positive samples.
    """
    
    user_info = pd.read_csv(FILTERED_USER_SOLVED_PROBLEM_PATH)
    user_info = user_info.rename(columns={'userName': 'user_id', 'problemId': 'item_id'})
    user_info['rating'] = 1  # Assigning a positive rating

    problem_info = pd.read_csv(FILTERED_PROBLEM_PATH)
    problems = problem_info["problemId"].tolist()

    users = user_info['user_id'].unique()
    negative_samples = []

    # Generate negative samples for each user
    for user in tqdm(users):
        solved_problems = user_info[user_info['user_id'] == user]['item_id'].tolist()
        unsolved_problems = [problem for problem in problems if problem not in solved_problems]
        random.shuffle(unsolved_problems)

        num_negative_samples = int(len(solved_problems) * negative_proportion)
        sampled_negatives = unsolved_problems[:num_negative_samples]
        negative_samples.extend([[user, problem] for problem in sampled_negatives])

    # Create DataFrame for negative samples and merge with positive samples
    negative_sample_df = pd.DataFrame(negative_samples, columns=["user_id", "item_id"])
    negative_sample_df['rating'] = 0

    merged_data = pd.concat([user_info, negative_sample_df], ignore_index=True)
    merged_data.to_csv(MERGED_DATA_PATH, index=False)


if __name__ == "__main__":
    filter_problems(threshold=100)
    filter_user_solved_problems()
    perform_negative_sampling(negative_proportion=1.0)
