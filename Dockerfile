#Alpine linux is lightweight and sufficient for this project
FROM alpine
MAINTAINER "William Michalak <wmichalak@gmail.com>"
FROM continuumio/miniconda3
#
# make directories to hold application files
RUN mkdir -p /root/kinetics/ && \
    mkdir -p /root/Simulations/Outputs

WORKDIR /root/kinetics/

# copy contents from your local to your docker container
COPY . /root/kinetics/

# Install conda environment
ADD environment.yml /tmp/environment.yml
RUN conda env create -f environment.yml && \
    conda clean --all && \
    echo "source activate kineticsenv" > ~/.bashrc
ENV PATH /opt/conda/envs/kineticsenv/bin:$PATH


