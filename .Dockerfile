# 기본 이미지 선택
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye
RUN apt-get update

# 작업 디렉토리 설정
RUN mkdir -p /oppt/ml/code
WORKDIR /opt/ml/code

# 필요한 Python 라이브러리 설치
COPY . .
RUN pip install -r requirements.txt

# Python 스크립트 복사
ENV AWS_ACCESS_KEY_ID GOOD MORNING!
ENV AWS_SECRET_ACCESS_KEY GOOD EVENING!
ENV AWS_DEFAULT_REGION GOOD NIGHT!

# 스크립트 실행을 위한 기본 명령어 설정
# EXPOSE 8080
# ENTRYPOINT ["./run.sh"]
