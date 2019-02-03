# README #

This User Guide demonstrates how to set up a Python Cantera development environment inside a Docker container. I wrote this as a reminder
for myself and to share with anyone else interested. Before I get started, let's review why you would want to use a container environment.
The reasons to use Cantera inside of a container are, but not limited to:
1. If you want to build your code on one computer and run it on another.
    1. Avoid installation issues related to different platforms (Windows, Linux, MacOS). 
    2. Avoid maintaining Python distributions across different machines and worrying about conflicts and dependencies. 
    3. Avoid maintaining local code repositories across different machines. 
2. I have had issues with multiple cantera installations on a single machine and this approach is assured to create a barrier between systems.

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
could be filled with many *.py files and simulations. Here, I only include a two examples: catalytic_combustion.py and multiprocessing_viscosity.py.
 The former is an exact copy from the Cantera repo; the latter has some modifications to demonstrate how the parallelism improves
 with the number of calculations. 
 
 You will need two additional files at the root of the folder called 
`Dockerfile` and `environment.yml`. We will review the use of these files later.


#### Create a Dockerfile ####

The Dockerfile contains the recipe for building the container. First, we need to define the Linux distro for the container. 
I use the lightweight Alpine distribution with python 3.6. I also import miniconda3 to manage the Python packages.

```
FROM python:3.6-alpine
MAINTAINER "William Michalak <wmichalak@gmail.com>"
FROM continuumio/miniconda3
```

Next, we need to define the folder structure in the container. I use a folder called kinetics to house the Cantera code
and set this as my working directory. We also need a folder to hold the simulation outputs.

```
RUN mkdir -p /root/kinetics/ && \
    mkdir -p /root/Simulations/Outputs
WORKDIR /root/kinetics/
```

With the folder structure in place, we can copy the contents of the local simulation files into the container. Note that 
the COPY command will only work in the current local directory. I have tried to also COPY from folders higher in the folder structure, but
this does not work. I will show another way to copy files later on.
```
COPY . /root/kinetics/
```

We can install the Python packages including Cantera and let Conda do the work of figuring out dependencies. We use
an `environment.yml` file to define the packages. I also follow best practices and install into a virtual environment called 
`kineticsenv`.  Finally, I activate `kineticsenv', so that when we enter into the container, we are ready to go!

```
# Install conda environment
ADD environment.yml /tmp/environment.yml
RUN conda env create -f environment.yml && \
    conda clean --all && \
    echo "source activate kineticsenv" > ~/.bashrc
ENV PATH /opt/conda/envs/kineticsenv/bin:$PATH
```

Note that the environment name, kineticsenv, is defined in the `enviroment.yml` file. 

Another useful and non-obvious aspect is how I constructed the RUN statements. Docker takes each command in the Dockerfile
and builds a layer for that command. More commands equals more layers equals bigger image. Place the commands under as 
few RUN statements as possible serves us with smaller images.

### Build the Docker Image ###

Now that we have defined the Dockerfile, we can build the Docker image. Navigate to the folder location in Terminal and run:

```
$ docker build -t=cantera .
```

with the `.` at the end to signal that we are building from the current directory. 

Docker will search for a file called Dockerfile and run it. I use the `-t=cantera` flag to tag the Docker image, so that we can 
refer to it as _cantera_ later on. This will take a few minutes to download Alpine,
 miniconda, and all of the python packages. This one command will create the 
Container, which we will be able to run shortly. 

Let's take stock of the situation. We have built an image based in Linux
that has Python and all of the dependencies required to run Cantera as well as other data science, engineering, modeling 
libraries we may need (Pandas, Scipy, and Matplotlib). And, we can send this 
image to any machine we desire and it will work. We never have to reinstall Python or Cantera again! If we have 
new code or a modified simulation, we can just copy it into a container deployed from the image (or rebuild image) and run it.

Let's also review the difference between an image and container. A container is launched by running an image. 
An image is an executable package that includes everything needed to run an application–the code, a runtime, libraries, 
environment variables, and configuration files.
A container is a runtime instance of an image–what the image becomes in memory when executed (that is, an image with state, 
or a user process). You can see a list of your running containers with the command, docker ps, just as you would in Linux. 
— from [Docker Concepts](https://docs.docker.com/get-started/#docker-concepts)

### Run the Cantera Container ###

To run the container we type:

```
$ docker run -it --name kinetics kinetics
```

The the `-it` flag tells docker to start the container in the interactive and pseudo TTY mode, respectively.
 We will now be at a shell prompt with the conda virtual environment activated inside of the container. 
(Continue reading __Where is my data?__ before actually running this line.) The `--name kinetics` flag defines the name of the running
container. The second `kinetics` is the name of the image. If the `--name` is not defined, Docker will assign a name. In this case
I usually refer to the container by the Container ID.

### Run a Cantera Simulation ###

In interactive mode, we enter into the container at the working directory, where our code is located. We
can enter our typical unix commands: `ls, pwd, cd ...` at this time. Note, that the container is light and isn't meant to be a full-fledged Linux 
 environment, so we won't be able to edit code, for example. Also note, the format of the prompt. First is the conda environment name, 
followed by the user name (root), the container tag ID, and then the folder location, separated by a : and completed
by a #.  We can now run the cantera simulation:

```
(kineticsenv) root@<tag>:~/kinetics# python cantera_PBR.py 
```

Viola! We were able to run our Cantera simulation in the kinetics container! We can check if the simulation completed successfully
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

If you want to leave the container running you type `ctrl+p,ctrl+q`. Otherwise, exiting will kill the container.

### Run, Start, Attach, and Stop ###

When you use the `docker run` command, you are instantiating a container and starting it up in one command. As shown before, 
you can use the `-it` command to enter into interactive shell. Without the `it` flags, the container will start and run until all commands are completed. 
In our case, we haven't defined any commands to run on startup, so this container will automatically exit.  In my case, I usually will 
enter in the interactive mode and this won't be a problem. For the sake of documentation, it is also worth noting that you 
can start a docker container to run in background using the `-d` flag,, which stands for _detach_,
If the container is started in the detached mode and is running, we can enter into the container, or attach, as discussed below. 
We also can reattach if the container is running after the `ctrl+p,ctrl+q` commands. 

To start, or attach into a container, we usually need to identify that it is running and the ID using:

```
$ docker ps -all
```

Fields are shown with Container ID, IMAGE, COMMAND, CREATED, STATUS, PORTS, NAMES will be printed. This will show you
 all available (active and inactive) containers. We can then start, attach, and stop the container with the commands

```
$ docker start <CONTAINER_ID>
$ docker attach <CONTAINER_ID>
$ docker stop <CONTAINER_ID>

or 

$ docker start <NAME>
$ docker attach <NAME>
$ docker stop <NAME>
```

### Cleaning up containers ###
As we experiment, we will  want to clear out the old images, containers and volumes:

```
$ docker system prune --volumes
$ docker image prune
$ docker image rm <CONTAINER ID>
```

We can also force the container to be removed by adding `-rm` in the `docker run` call. To clean up all containers and images
on the system, you can type `docker rmi $(docker images -q)`

### Where is my data? ###

Containers are ephemeral and stateless by default. We start them up, run our code, shutdown and everything disappears. This works
fine if you are running a webserver from a container (see numerous examples coupling Flask and nginx). Unfortunately, this means we also
lose any created data. The solution to this is to create a __Volume__; a pipeline between the container and the Host machine. 
In order to do this, we modify the docker run command as:

```
$ docker run -it --name kinetics -v <local directory>:/root/Simulations/Outputs kinetics
```

This will create a pipeline between the two directories. Anything that you place into the `<local directory>` will be made
available in the `/root/Simulations/Outputs` directory in the container and vice versa. 

The volume mechanism is also a reasonable way to introduce another model into a container without having to rebuild. Frankly, we 
could store all of our models in the Host volume and run them from within the container. 

### Spinning up and executing in the background ###

Starting this container in the background is not particularly useful because there are no commands that will be run. There are 
two mechanisms to start the container in the background and execute a simulation.

#### Executing commands (EXEC) onto a running container ####

If you have booted your container and it is running in the background (with a `-d` flag or if you used `docker start`)
and you want to execute a command, you can use the `docker exec` command:

```
$ docker container exec <CONTAINER ID> python cantera_PBR.py
```

Note how we use spaces between the commands.


#### Using an ENTRYPOINT ####

We can also spin up the container and define what to run first by adding the commands we want to run
on the end of the statement. This is defining the entrypoint.

```
$ docker run -d --name cantera -v <local directory>:/root/Simulations/Outputs kinetics python cantera_PBR.py
```

### Copying files between Host and Container ###

We can copy files from container to host by

```
$$ docker cp <container>:/path/to/file.ext .
```

Or copy a file from the host to the container

```
$$ docker cp file.ext <container>:/path/to/file.ext
```

These files will only be present as long as the container is running. Once a container is killed, these files will be lost. 
In order to save the files added to the container, we need to commit and save the container to the image.

### Docker Commit  ###

To commit the changes type:

```
$ docker commit <CONTAINER_NAME> kinetics
```

We can also choose to make a new container on the commit and call it something other than kinetics.

### Deploy on a Remote Machine ###

I often want to deploy a set of simulations onto a remote server (really, this is why I am using containers). 
Without having to rebuild the container all over again, we can just save the image and use secure copy protocol to transfer it.

In the terminal on your local machine save the container image:

```
$ docker save --output kinetics.tar kinetics
```

Transfer image files over to a server using SCP commands:

```
$ scp kinetics.tar <user>@<remote server>:/path/to/directory
```

The size of this container is about 3 GB despite my intentions to keep the container light; this is due to the Python libraries. 
Without Python+libraries, the container is around 500 MB. Once the file has transferred, we can ssh into the server. Fortunately, we
should not need to rebuild or transfer the container often. Using the Volumes also us to run new code without rebuilding.

To load the image we unpack the tar: 

```
$ sudo docker load --input kinetics.tar
```

where I use `sudo` because I am not the root/admin on the server. You may also need to change permissions `$ chmod u+x kinetics`. 

We are now ready to run the container on the remote machine just as we did before.

```
$ docker run -it -v <local directory>:/root/Simulations/Outputs kinetics
```

If you experience difficulties or you have suggestions, please reach out to wmichalak@gmail.com.

### References ###

I found these two sites helpful when learning about Docker.

[Docker cheat sheet](https://github.com/wsargent/docker-cheat-sheet)

[Docker tutorial](https://rominirani.com/docker-tutorial-series-a7e6ff90a023)
