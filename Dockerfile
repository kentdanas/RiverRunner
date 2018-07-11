FROM ubuntu:16.04

# Update packages
RUN apt-get update -y

# Install packages
RUN apt-get install -y curl
RUN apt-get install -y bzip2
RUN apt-get install -y awscli
RUN apt-get install -y python-pip

# Install Conda
RUN curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=${PATH}:/miniconda/bin
RUN conda update -y conda

# Setup environment
RUN conda create -n rr python=3.6
ENV PATH=/miniconda/envs/rr/bin:${PATH}

# Add and install Python modules
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt

# Bundle app source
ADD . /src

# Set environment variables
ENV GEOLOCATION_API_KEY=$GEOLOCATION_API_KEY
ENV DARK_SKY_KEY=$DARK_SKY_KEY
ENV MAPBOX_KEY=$MAPBOX_KEY
ENV DB_DRIVER=$DB_DRIVER
ENV DB_HOST=$DB_HOST
ENV DB_MAIN=$DB_MAIN
ENV DB_PASS=$DB_PASS
ENV DB_PORT=$DB_PORT
ENV DB_USER=$DB_USER

# Expose
EXPOSE 5000

# Run
CMD ["python", "/src/application.py"]