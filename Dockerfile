FROM ubuntu:16.04

# Update packages
RUN apt-get update -y

# Install Conda
RUN curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh

# setup environment
RUN conda create -n rr python=3.6
RUN source activate rr

# Install pip
RUN apt-get install -y python-pip

# Add and install Python modules
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt

# Bundle app source
ADD . /src

# Expose
EXPOSE $PORT

# Run
CMD ["python", "/src/application.py"]