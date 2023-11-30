FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

sudo apt-get -y update
sudo apt -y install wget
sudo apt -y install unzip
sudo apt -y install curl
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt -y install ./google-chrome-stable_current_amd64.deb
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/` curl -sS https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64`/chromedriver-linux64.zip
sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/bin

