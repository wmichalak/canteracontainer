# README #

This User Guide demonstrates how to set up a Python Cantera development environment inside a container. I wrote this as a reminder
for myself and anyone else interested. Before I get start, let's review why you would want to use a container environment.
The reasons to use Cantera inside of a container are:
1. Avoid installation issues related to different platforms. 
2. Avoid maintaining Python distributions across different machines and worrying about conflicts and dependencies. 
3. Avoid maintaining code repositories across different machines. 
4. I have had issues with multiple cantera installations on a single machine and this approach is assured to create a barrier between systems.

### Cantera ###

The code in this repo uses Cantera 2.4. This guide is not meant to demonstrate how to use Cantera. If you want to know more
 see [Cantera documention](https://cantera.org/documentation/) for details AND search through the [Cantera user group](
 https://groups.google.com/forum/#!forum/cantera-users). There is a good chance someone has run into the same issue you 
 are having and, if not, the developers are friendly and active if you need help.

### Containers ###

This guide was developed using Docker Community edition Version 2.0.0.2 to build and orchestrate the container. 
To install Docker, follow the [Docker Installation Guides](https://docs.docker.com/install/). You will need to setup Docker
on each machine that will run the container.

### Folder Structure ###

The root folder of the repository contains only a few files in order to demonstrate the implementation. Of course, the folder
could be filled with many simulations. Here, I only include a single file that simulates a Packed Bed Reactor called 
`cantera_PBR.py`. You will need two additional files at the root of the folder called 
`Dockerfile` and `environment.yml`. We will review the use of these files later.

### Building the Cantera Container ###

#### Create a Dockerfile ####

The Dockerfile contains the recipe for building the container. First we need to define the Linux distro for the container. 
I use the lightweight alpine distribution with python 3.6. I also import miniconda3 to manage the Python packages.

```
FROM python:3.6-alpine
MAINTAINER "William Michalak <wmichalak@gmail.com>"
FROM continuumio/miniconda3
```

Next, we need to define the folder structure in the container. I use a folder called kinetics to house the Cantera code
and set this as my working directory.

```
RUN mkdir -p /root/kinetics/
WORKDIR /root/kinetics/
```

We need a folder to hold the simulation outputs:

```
# make directories for output files
RUN mkdir -p /root/Simulations/Outputs
```

With the folder structure in place, we can copy the contents of the local simulation files into the container. Note that 
the COPY command will only work for local files. I have tried to also COPY from folders higher in the folder structure, but
this does not work. I will show another way to copy files later on.
```
COPY . /root/kinetics/
```

We can install the Python packages including Cantera and let Conda do the work of figuring out dependencies. We use
an `environment.yml` file to define the packages. I also follow best practices and install into a virtual environment called 
`kineticsenv`.  Finally, I activate `kineticsenv', so that when we enter into the container, we are ready to go!

```
ADD environment.yml /tmp/environment.yml
RUN conda env create -f environment.yml
RUN echo "source activate kineticsenv" > ~/.bashrc
ENV PATH /opt/conda/envs/kineticsenv/bin:$PATH
```

Note that the environment name is defined in the `enviroment.yml` file 

### Build the Container ###

First, we build the Docker container. Navigate to the folder location in Terminal and run:

```
docker build -t=kinetics .
```

Docker will search for a file called Dockerfile and run it. I use the `-t=kinetics` flag to tag the Docker image, so that we can 
refer to it as kinetics later on. This will take a few minutes to download Alpine,
 miniconda, and all of the python packages. This one command will create the 
Container, which we will be able to run shortly. 

Let's take stock of the situation. We have built a container based in Linux
that has all the Python and dependencies required to run Cantera as well as other data science, engineering, modeling,
and simulations we may ever need to do (I included Pandas, Scipy, and Matplotlib in the container as well!). And, we can send this 
container to any machine we desire and it will work. We never have to reinstall Python or Cantera again! If we have 
new code or a modified simulation, we can just copy it into the container and run it.

### Run the Cantera Container ###

To run the container we type:

```
docker run -it kinetics
```

The the `-it` flag tells docker to start the container in the interactive mode. We will now be at a shell prompt 
with the conda virtual environment activated inside of the container. 
(Continue reading __Where is my data?__ before actually running this line.) If you want to just build the container image 
in order to send it somewhere else, leave the __i__ flag out 

### Run a Cantera Simulation ###

We enter into the container at the working directory, where our code is located. We can then run the simulation! Before this, 
we can enter our typical unix commands: `ls, pwd, cd ...`. Note the format of the prompt. First is the conda environment, 
followed by the user name (root) in the container, given by its tag ID, and then the folder location, separated by a : and completed
by a #. 

```
(kineticsenv) root@<tag>:~/kinetics# python cantera_PBR.py 
```

Viola! We were able to run our Cantera simulations in the kinetics Container! We can check if the simulation completed successfully
by navigating to our Simulations/Outputs directing and looking for our output file.

```
(kineticsenv) root@<tag>:~/kinetics# cd ~/Simulations/Outputs
(kineticsenv) root@<tag>:~/Simulations/Outputs# ls
output.csv
```

We can exit the container by typing 
```
(kineticsenv) root@<tag>:~/Simulations/Outputs# exit
```

### Where is my data? ###

Containers are ephemeral. We start them up, run our code, shutdown and everything disappears. Unfortunately, this means we also
lose any created data. The solution to this is to create a __Volume__; a pipeline between the container and the Host machine. 
In order to do this, we modify the docker run command as:

```
docker run -it -v <local directory>:/root/Simulations/Outputs kinetics
```

This will create a pipeline between the two directories. Anything that you place into the `<local directory>` will be made
available in the `/root/Simulations/Outputs` directory in the container and vice versa. Others that have used containers 
before will note that VOLUMES can be defined in the DOCKERFILE. I have not found this to work.

### Start, attach, and stop ###

When you `exit` out of the container, the container image still exists and we do not need to rebuild it. In order to start up
the container again we need to identify the container image ID. We can do this with

```
docker ps -all
docker start <CONTAINER_ID>
docker attach <CONTAINER_ID>
```

 `docker attach`  will bring you back into the container shell

### Copying files between Host and Container ###

We can copy files from container to host by

```
docker cp <container>:/path/to/file.ext .
```

Or copy a file from the host to the container

```
docker cp file.ext <container>:/path/to/file.ext
```

### Deploy on a Remote machine ###

I often want to deploy a set of simulations onto a remote server. Without having to rebuild the container all over again, 
we can just save the image and use secure copy protocol to transfer it.

In the terminal on your local machine 
```
$ docker save --output kinetics.tar kinetics
```

Transfer image files over to server using SCP commands:

```
-$ scp <image> <USER>@sil-sf-webvm-1.siluria.private:<folder name>
OR
-$ scp kinetics.tar <user>@<remote server>:/path/to/directory
```

The size of this container is about 3 GB depsite trying to keep the container light; this is due to the Python libraries. 
Without python the container is around 500 MB. Once the file has transferred, we can ssh into the server.

To load the image we unpack the tar: 

```
-$ sudo docker load --input kinetics.tar
```

where I use `sudo` because I am not the root/admin on the server. You may also need to change permissions `$ chmod u+x kinetics`. 

We are now ready to run the container on the remote machine just as we did before.

```
docker run -it -v <local directory>:/root/Simulations/Outputs kinetics
```

If you experience difficulties or think that I should add something, please let me know at wmichalak@gmail.com.

### References ###

I found these two sites helpful when learning about Docker.

https://github.com/wsargent/docker-cheat-sheet
https://rominirani.com/docker-tutorial-series-a7e6ff90a023
