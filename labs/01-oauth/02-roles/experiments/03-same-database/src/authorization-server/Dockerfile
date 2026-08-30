FROM python:3.14-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY app /code/app
COPY tests /code/tests

EXPOSE 8300

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8300"]