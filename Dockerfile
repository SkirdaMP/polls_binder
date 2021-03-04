FROM python:3.8
# install the notebook package
RUN pip install --no-cache --upgrade pip && \
    pip install --no-cache notebook

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}

COPY ./requirements.txt ${HOME}/requirements.txt

RUN pip install -r requirements.txt

USER ${USER}


FROM postgres:12

ENV POSTGRES_PASSWORD = postgres \
    POSTGRES_USER = postgres \
    POSTGRES_DB = polls

ADD database/create_db.sql /docker-entrypoint-initdb.d
