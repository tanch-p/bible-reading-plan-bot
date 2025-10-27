# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv
FROM python:3.12-slim-trixie

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy your bot code
COPY . .

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

# Default command
CMD ["uv", "run", "main.py"]
