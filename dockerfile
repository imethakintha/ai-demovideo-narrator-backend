# Python 3.10 image එකක් පාවිච්චි කරමු
FROM python:3.10-slim

# System dependencies (FFmpeg අනිවාර්යයි)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Requirements install කිරීම
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Project files copy කිරීම
COPY . .

# Permissions ලබා දීම (Uploads/Outputs folders වලට)
RUN mkdir -p /code/uploads /code/outputs /code/temp && chmod -R 777 /code

# HF Spaces වැඩ කරන්නේ port 7860 හි බැවින් එය expose කරන්න
EXPOSE 7860

# ඇප් එක run කිරීම
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]