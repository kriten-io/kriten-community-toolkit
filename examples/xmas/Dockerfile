FROM python:3.9-slim
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["python", "xmas.py"]
# To test:
# export EXTRA_VARS='{"from": "Steve"}'
# docker run -e EXTRA_VARS evolvere/kritren-xmas:0.1
