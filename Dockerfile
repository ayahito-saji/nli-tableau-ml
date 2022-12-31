FROM pytorch/pytorch:nightly-runtime-cuda9.2-cudnn7

RUN apt-get update -y &&\
    apt-get upgrade -y

RUN pip install --upgrade pip && pip install --upgrade setuptools && \
    pip uninstall -y torch-nightly &&\
    pip install torch==1.4.0+cu92 torchvision==0.5.0+cu92 -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install jupyterlab

WORKDIR /notebooks

CMD jupyter-lab --ip 0.0.0.0 --port 8888 --allow-root

EXPOSE 8888
