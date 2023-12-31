# Gachon-boj-recommendation

lang: [🇰🇷 한국어](https://github.com/Orca0917/Gachon-boj-recommendation) | [🇺🇸 ENGLISH](https://github.com/Orca0917/Gachon-boj-recommendation/blob/main/README-us.md)

안녕하세요, 본 레포지토리는 가천대학교 학생들을 위한 백준 알고리즘 문제추천을 주제로 한 웹 서비스 프로토타입에 대한 코드를 담고 있습니다. 실제로 서비스를 진행하기 위해서는 별도의 AWS관련 계정 설정정보와 데이터셋의 준비가 필요합니다. 문제가 될 수 있어 데이터셋은 레포지토리에 포함시키지 않은 부분 양해해주시기 바랍니다.

본 웹서비스는 [https://gachonboj.kro.kr](https://gachonboj.kro.kr)에 접속해서 사용할 수 있으며 현재는 가천대학교 학생들을 대상으로만 서비스를 진행하고 있습니다. 12월 초까지만 서비스가 진행될 예정이며, 이후에 다시 준비되는대로 공지해드리겠습니다.

<p align="center">
<img src="https://github.com/Orca0917/Gachon-boj-recommendation/assets/91870042/09f42896-a21f-4d80-bfdc-af547d455c2e" />
</p>



## Structure

해당 프로젝트는 다음과 같은 구조를 갖고 있습니다.
```
📦 GACHON-BOJ-RECOMMENDATION
├─ 📂 asset
│  ├─ 📄 mappig.pickle
│  ├─ 📄 matrix_factorization.pickle
│  └─ 📄 user_based_collaborative_filtering.pickle
├─ 📂 crawler
│  ├─ 📜 gachon_solvedac.py
│  ├─ 📜 gachon_user.py
│  ├─ 📜 problem_tier.py
│  ├─ 📜 problem.py
│  └─ 📜 solvedac_each_300.py
├─ 📂 data
├─ 📂 module
│  ├─ 📜 CBCF.py
│  ├─ 📜 MF.py
│  ├─ 📜 preprocess.py
│  ├─ 📜 UBCF.py
│  └─ 📜 utils.py
├─ 📜 app.py
├─ 📜 config.py
├─ 📄 requirements.txt
└─ 📄 READMe.txt
```
©generated by [Project Tree Generator](https://woochanleee.github.io/project-tree-generator)


- asset 폴더는 학습이 완료된 모델의 파라미터 파일 또는 행렬 정보를 담고 있습니다.
- crawler 폴더는 백준 웹사이트로부터 크롤링하기 위한 코드를 담고 있습니다.
- data 폴더는 크롤링이 완료된 데이터가 저장되는 폴더입니다.
- module 폴더는 동작하는 실제 알고리즘들을 담고 있습니다.

<br>

## Web: Streamlit
프론트엔드는 `Streamlit`을 사용해 프로토타입 버전으로 작성되었으며, 사이드바에서 사용할 알고리즘을 선택할 수 있습니다. [백준](https://noj.am)에서 사용중인 아이디를 입력하시면 사용자 정보에 맞는 문제를 5개 추려서 전달드립니다.

![image](https://github.com/Orca0917/Gachon-boj-recommendation/assets/91870042/5393dbc0-bfd6-4343-a8d5-cbf57fa0b147)

Streamlit의 실행을 위해 아래와 같이 구현합니다. 필요에 따라, AWS환경의 경우 8501번 포트에 대한 인바운드르 개방해야할 수 있습니다.

```absh
streamlit run app.py
```

<br>


## ML Algorithms

해당 프로젝트에 적용된 알고리즘은 딥러닝을 사용하지 않은 머신러닝 알고리즘으로, 3가지가 사용되었습니다.

- Matrix factorization
- User-based collaborative filtering
- Content-based collaborative filtering

각 알고리즘에 대한 설명은 아래를 참고해주시기 바랍니다.

<br>

### Matrix factorization
Matrix factorization(행렬 인수분해)알고리즘은 rating matrix 1개를 2개의 잠재 행렬로 나누고, 잠재 행렬의 내적이 rating matrix가 되도록 만드는 기법입니다. 아직 평점이 내려지지 않은 값에 대해 평점을 예측할 수 있습니다.

Rating matrix는 행(사용자), 열(문제)로 구성되어 있으며, 문제를 풀었으면 1이라는 값이 채워져있습니다. 각 유저별로, 푼 문제에 비례하여 `negative sampling`을 하여 아직 풀지 못한 값에 대해서도 0이라는 값을 데이터에 추가할 수 있게 하였습니다. 수식은 아래와 같습니다.

$$
R = UV
$$

모델의 평가지표로는 RMSE와 log loss를 사용했으며 RMSE의 값은 0.311, Log Loss 값은 0.484입니다.

$$ \text{RMSE} = \sqrt{\sum_{i=1}^n \frac{(\hat{y}_i - y_i)}{n}} \qquad \text{log loss}= y\log p+(1-y)\log (1-p)$$

<br>

### User based collaborative filtering

유저 기반 협업필터링 (UBCF)는 matrix factorization과 유사하게 rating matrix, 여기서는 user-item interaction matrix 정보를 사용하여 유사도를 계산합니다. 유사도는 pearson 유사도, Jaccard 유사도, Cosine 유사도에 대해 적용할 수 있으며 현재는 **Cosine 유사도**를 적용하여 서비스하고 있습니다. User-item matrix에 대해 자신의 문제풀이 이력과 가장 비슷한 유저 $N$명을 찾아 내가 아직 풀지 못한 문제들을 추천합니다.

<br>

### Content based collaborative filtering

컨텐츠 기반 협업필터링(CBCF) 에서는 사용자의 문제풀이 이력 이외의 정보를 사용합니다. 본 프로젝트에서 사용된 정보는 유저의 알고리즘 문제풀이 실력으로 [solved.ac](https://solved.ac)에서 사용자의 8가지 알고리즘에 대한 실력 정보를 수집하여 계산하였습니다. 사용된 알고리즘 정보는 다음과 같습니다.

- 수학, 구현, 그리디, 문자열, 자료구조, 그래프, 동적계획법, 기하

UBCF와 유사하게 해당 알고리즘 풀이실력과 가장 유사한 다른 유저를 찾아 문제를 추천하게 됩니다. 문제풀이 이력과는 별도로 점수로 측정되기 때문에 실력에 맞는 문제를 풀 수 있다는 장점이 있습니다.

<br>

## AWS Service Architecture

![image](https://github.com/Orca0917/Gachon-boj-recommendation/assets/91870042/323357b0-998d-45d2-b8e8-baa8ae26ccd8)

<br>

## Contributors

- 가천대학교 AI.소프트웨어학부(소프트웨어학과) 장원준
- 가천대학교 AI.소프트웨어학부(소프트웨어학과) 오명석
- 가천대학교 AI.소프트웨어학부(소프트웨어학과) 최수미
