FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

#CMD ["uvicorn", "main:app", "--reload" ]

#https://fastapi.tiangolo.com/deployment/manually/#install-the-server-program
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"] # It doesn't make sense to relaod inside docker, I think

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]




# Do we need to first make a requirements file and then install with
# RUN pip install -r requirements.txt or not because we already copied my existing pycharm project,
# which already has a venv folder

# docker build .
# docker images -a
# docker run -p 5000:5000 <image id>

# * Running on http://127.0.0.1:5000
# * Running on http://172.17.0.2:5000

#Go 127.0.0.1:5000/hello/sebastian/