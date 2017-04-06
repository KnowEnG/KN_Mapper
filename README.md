
[![Docker Repository on Quay.io](https://quay.io/repository/cblatti3/kn_mapper/status "Docker Repository on Quay.io")](https://quay.io/repository/cblatti3/kn_mapper)


# KN_Mapper
Download a subnetwork from the KnowEnG Knowledge Network

A repo for the `Dockerfile` to create a Docker image for the kn_mapper.py command. Also contains the
`Dockstore.cwl` which is used by the [Dockstore](https://www.dockstore.org) to register
this container and describe how to call kn_mapper for the community.


## Building Manually

Normally you would let [Quay.io](http://quay.io) build this.  But, if you need to build
manually you would execute:

    docker build -t quay.io/cblatti3/kn_mapper .


## Running Manually

```
# enter the docker container
$ docker run -it -w='/home/ubuntu' -v `pwd`:/home/ubuntu quay.io/cblatti3/kn_mapper:latest

# run command within the docker container
$ /home/src/kn_mapper.py /home/ubuntu/sample_ids.txt --redis_port 6380
```
You'll then see a map file, `sample_ids.node_map.txt`, in the current directory. The `-v` is used to mount this result out of the container.

## Running Through the Dockstore CLI

This tool can be found at the [Dockstore](https://dockstore.org/containers/quay.io/cblatti3/kn_mapper), login with your GitHub account and follow the
directions to setup the CLI.  It lets you run a Docker container with a CWL descriptor locally, using Docker and the CWL command line utility.


### Make a Parameters JSON

A sample parameterization of the kn_mapper tool is present in this repo in `kn_mapper.job.yml`:

```
infile:
  class: File
  location: sample_ids.txt
redis_host: knowredis.knowhub.org
redis_port: 6380
taxon: 9606
```

### Run with the CLI

Run it using the `dockstore` CLI:

```
Usage:
# fetch CWL
$ dockstore tool cwl --entry quay.io/cblatti3/kn_mapper:latest > Dockstore.cwl

# make a runtime JSON template and edit it (or use the content of kn_mapper.job.yml above)
$ dockstore tool convert cwl2json --cwl Dockstore.cwl > Dockstore.json

# run it locally with the Dockstore CLI
$ dockstore tool launch --entry quay.io/cblatti3/kn_mapper:latest --yaml kn_mapper.job.yml
```
