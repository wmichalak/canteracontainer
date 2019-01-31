#Alpine linux is lightweight and sufficient for this project
FROM python:3.6-alpine
MAINTAINER "William Michalak <wmichalak@gmail.com>"
FROM continuumio/miniconda3

# make directories to hold application files
RUN mkdir -p /root/kinetics/
WORKDIR /root/kinetics/

# make directories for output files
RUN mkdir -p /root/Simulations/Outputs

# copy contents from your local to your docker container
COPY . /root/kinetics/

# Install conda environment
ADD environment.yml /tmp/environment.yml
RUN conda env create -f environment.yml
RUN echo "source activate kineticsenv" > ~/.bashrc
ENV PATH /opt/conda/envs/kineticsenv/bin:$PATH

