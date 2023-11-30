import os
import boto3

class Config:

    def __init__(self):
        # -- data
        self.PROBLEM_INFO_DATA               = ("./data/problem_info_data.csv", "problem/problem_info_data.csv")
        self.PROBLEM_TIER_DATA               = ("./data/problem_tier_data.csv", "problem/problem_tier_data.csv")
        self.PROBLEM_DATA                    = ("./data/problem_data.csv", "problem/problem_info_data.csv")
        
        self.PREPROCESSED_PROBLEM_DATA       = ("./data/preprocessed_problem_data.csv", "problem/preprocessed_problem_data.csv")
        self.PREPROCESSED_GACHON_USER_DATA   = ("./data/preprocessed_gachon_user_data.csv", "user/preprocessed_gachon_user_data.csv")
        self.NEGATIVE_SAMPLED_USER_DATA      = ("./data/negative_sampled_user_data.csv", "user/negative_sampled_user_data.csv")

        self.GACHON_USER_DATA                = ("./data/gachon_user_data.csv", "user/gachon_user_data.csv")
        self.GACHON_USER_TIER_DATA           = ("./data/gachon_user_tier.csv", "user/gachon_user_tier.csv")
        self.GACHON_ALGORITHM_STATUS         = ("./data/gachon_algorithm_stats.csv", "user/gachon_algorithm_stats.csv")

        self.NECESSARY_DATA_FILES = [
            self.PROBLEM_INFO_DATA,
            self.PROBLEM_TIER_DATA,
            self.PROBLEM_DATA,
            self.PREPROCESSED_PROBLEM_DATA,
            self.PREPROCESSED_GACHON_USER_DATA,
            self.NEGATIVE_SAMPLED_USER_DATA,
            self.GACHON_USER_DATA,
            self.GACHON_ALGORITHM_STATUS
        ]


        # -- asset
        self.ASSET_BOJ_LOGO          = ("./asset/boj_logo.png", "asset/boj_logo.png")
        self.ASSET_MAPPING           = ("./asset/mapping.pickle", "asset/mapping.pickle")
        self.ASSET_MF                = ("./asset/matrix_factorization.pickle", "asset/matrix_factorization.pickle")
        self.ASEST_UBCF              = ("./asset/user_based_collaborative_filtering.pickle", "asset/user_based_collaborative_filtering.pickle")

        self.NECESSARY_ASSET_FILES = [
            self.ASSET_BOJ_LOGO,
            self.ASSET_MAPPING,
            self.ASSET_MF,
            self.ASEST_UBCF
        ]

        self.validate()

    def validate(self):
        os.makedirs("./data", exist_ok=True)
        os.makedirs("./asset", exist_ok=True)

        # -- check data & asset files
        data_files = [f for f in os.listdir("./data") if os.path.isfile(os.path.join("./data", f))]
        for data_file in self.NECESSARY_DATA_FILES:
            if data_file[0].split("/")[-1] not in data_files:
                # S3 리소스 생성
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                    region_name=os.environ['AWS_DEFAULT_REGION']
                )
                s3.download_file('gachon-boj-s3', data_file[1], data_file[0])
                

        asset_files = [f for f in os.listdir("./asset") if os.path.isfile(os.path.join("./asset", f))]
        for asset_file in self.NECESSARY_ASSET_FILES:
            if asset_file[0].split("/")[-1] not in asset_files:
                # S3 리소스 생성
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                    region_name=os.environ['AWS_DEFAULT_REGION']
                )
                s3.download_file('gachon-boj-s3', asset_file[1], asset_file[0])
        

    


