FROM python:3.6

RUN pip install -U pip setuptools && pip install jupyter

WORKDIR /notebooks

CMD jupyter notebook --port 8888 --ip 0.0.0.0 --allow-root

EXPOSE 8888
