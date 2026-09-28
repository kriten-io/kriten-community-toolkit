FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN ansible-galaxy collection install arista.eos