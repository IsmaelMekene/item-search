FROM python:3.8.15

WORKDIR /Users/me_teor21/Workspace/item-search

COPY requirements.txt ./

RUN pip install -r requirements.txt 

COPY search.py ./

COPY app.py ./

COPY constants.py ./

# COPY . .

ENTRYPOINT ["python", "app.py"]