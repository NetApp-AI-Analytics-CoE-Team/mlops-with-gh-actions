FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN pip install pillow
RUN pip install numpy
RUN pip install requests
RUN pip install typing

COPY ./app /app

# sudo docker build . -t kyonsy0722/my-fastapi:<ver>
# sudo docker push kyonsy0722/my-fastapi:<ver>