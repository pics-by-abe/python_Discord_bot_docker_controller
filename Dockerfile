FROM python:3.11.4-slim-buster

# Path: /bot
WORKDIR /bot

# Path: /bot
COPY requirements.txt .
# install dependencies
RUN pip install -r requirements.txt

# copy src
COPY src/ .

# run bot
CMD ["python", "bot.py"]
