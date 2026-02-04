# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

LABEL authors="theovanstratum"


# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the dependencies file to the working directory
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
# We add --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code to the working directory
COPY app.py .

# 6. Make port 8501 available to the world outside this container
EXPOSE 8501

# 7. Define the command to run the app
# --server.address=0.0.0.0 makes it accessible externally
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]