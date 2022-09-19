FROM python:3.10-slim
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
ENTRYPOINT ["python", "./pv_animation.py"]
