# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Update and install system dependencies
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        unzip \
        git \
        wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and NPM (if needed for any JS dependencies)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir -U pip \
    && pip3 install --no-cache-dir -U -r requirements.txt

# Copy application code
COPY . .

# Expose port if needed (optional for Telegram bots, usually not)
# EXPOSE 8080

# Run the start script
CMD ["bash", "start"]
