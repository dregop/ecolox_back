#!/bin/bash

# start docker for db
docker start online-exam-db

# start flask app
export FLASK_APP=./src/main.py
source .venv/Scripts/activate
flask run --debug


# docker run --name online-exam-db \
#     -p 5432:5432 \
#     -e POSTGRES_DB=online-exam \
#     -e POSTGRES_PASSWORD=0NLIN3-ex4m \
#     -d postgres


# connect to db : 
# docker exec -it 0ab38abd1781 psql -U postgres -W -d online-exam

 # drop table user:
#  drop table "user";
