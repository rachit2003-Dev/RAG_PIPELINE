# ----------------------------
# Base Image
# ----------------------------
FROM python:3.11-slim

# ----------------------------
# Set working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Copy files into container
# ----------------------------
COPY . /app

# ----------------------------
# Install dependencies
# ----------------------------
RUN pip install --upgrade pip && pip install -r requirements.txt

# ----------------------------
# Expose port
# ----------------------------
EXPOSE 8000

# ----------------------------
# Default command to run the API
# ----------------------------
CMD ["python", "main.py"]
