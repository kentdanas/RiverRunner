FROM ubuntu:16.04

# Update packages
RUN apt-get update -y && apt-get install -y curl

# Install Conda
RUN curl -O http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=$PATH:/miniconda/bin
RUN conda update -y conda

# Setup environment
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