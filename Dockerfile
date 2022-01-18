FROM pytorch/pytorch:nightly-runtime-cuda9.2-cudnn7

RUN pip install -U pip setuptools && pip install jupyter

WORKDIR /notebooks

CMD jupyter notebook --port 8888 --ip 0.0.0.0 --allow-root

EXPOSE 8888
