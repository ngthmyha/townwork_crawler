# Use x86 Ubuntu base image for compatibility
FROM ubuntu:24.04

# Update the system and install necessary tools and dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    gnupg \
    curl \
    unzip \
    chromium-browser \
    build-essential \
    python3-pip \
    python3-dev \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libgbm1 \
    libasound2-data \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    fonts-liberation \
    libxcursor1 \
    xdg-utils \
    ca-certificates \
    libappindicator3-1 \
    libdbusmenu-glib4 \
    libdbusmenu-gtk3-4 \
    libatk1.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libxss1 \
    libxtst6 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# # Add the Google Chrome repository for x86 compatibility
# RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
#     && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.83/linux64/chromedriver-linux64.zip \
    && unzip -o chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Add the Deadsnakes repository for newer Python versions
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update

# Set Python 3 as the default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy project files
WORKDIR /app
COPY . /app

# Kiểm tra nếu không có pyproject.toml thì khởi tạo Poetry
RUN test -f pyproject.toml || poetry init -n
RUN poetry install --no-root

# Copy dependency management files
COPY pyproject.toml poetry.lock /app/

WORKDIR /app/crawler

# Install dependencies using Poetry
RUN poetry add six selenium scrapy pymysql

# Use xvfb to enable GUI-less browser execution
ENV DISPLAY=:99