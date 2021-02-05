FROM ubuntu:18.04

# Install Needed Software
RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y software-properties-common strace

RUN apt-get install -y vim python3 python3-pip python3-venv

RUN add-apt-repository -y ppa:ubuntugis/ppa

RUN apt-get update && apt-get install -y gdal-bin python-gdal python3-gdal

#RUN apt-get install gdal-bin python3-gdal

# Prepare Filesystem
RUN mkdir /input

RUN mkdir /output

RUN mkdir /rpp

WORKDIR /rpp

# Add code and files to container
ADD . /rpp

RUN rm -rf venv

# Set necessary environment variables
ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8

# Install Python requirements for project
RUN pip3 install -r requirements.txt

# Use pip to install _this_ project
RUN pip3 install -e .

# Run processing chain script through shell script
ENTRYPOINT ["/bin/bash"]

#ENTRYPOINT ["find", "/Volumes/MacDrive/Working Memory/Level2A_Samples", "-maxdepth", "2", "-name", "*MTD*.xml", "|", "parallel", "gdalinfo", "{}", "|", "grep", "SUBDATASET_1_NAME", "|", "awk", "-F", "=", "{print $2}"]

#ENTRYPOINT ["/bin/bash", "create_index_rasters_from_dir.sh", "/rast", "/output"]
