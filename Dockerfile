FROM ubuntu:16.04

# Update packages
RUN apt-get update -y && apt-get install -y curl
RUN apt-get install -y bzip2 && apt-get install -y awscli

# Install Conda
RUN curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=${PATH}:/miniconda/bin
RUN conda update -y conda

# Setup environment
RUN conda create -n rr python=3.6
ENV PATH=/miniconda/envs/rr/bin:${PATH}

# Install pip
RUN apt-get install -y python-pip

# Add and install Python modules
ADD requirements.txt /var/app/requirements.txt
RUN cd /var/app; pip install -r requirements.txt

# Bundle app source
ADD . /var/app

# Move settings file
ENV AWS_ACCESS_KEY_ID=$AWSEBS_ID
ENV AWS_SECRET_ACCESS_KEY=$AWSEBS_KEY
CMD aws s3 cp s3://elasticbeanstalk-us-east-1-701856502070/RiverRunners/config/settings.py /var/app/riverrunner

# Expose
EXPOSE 5000

# Run
CMD ["python", "/var/app/application.py"]