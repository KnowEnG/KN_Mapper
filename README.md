![Docker Build Status](https://img.shields.io/docker/build/knoweng/kn_mapper.svg?style=flat-square)

# KN_Mapper
Tool for mapping gene identifiers to identifiers used in the KnowEnG Knowledge Network by querying the KnowNet Redis Database.

This repo contains the Python3 `kn_mapper.py` script that performs the entity mapping, a 
`Dockerfile` to create a Docker image, and a `Dockstore.cwl` that is used by the [Dockstore](https://www.dockstore.org) 
to register the corresponding Docker image container and describe how to call kn_mapper for the community.

## Usage

#### Inputs
The input to this tool is a file of gene identifiers or property identifiers, separated one per line. Example input files, `sample_genes.txt` and `sample_props.txt`, can be found in this repository.

#### Outputs
The output is by default a tab separated file with the file suffix '*.node_map.txt' with 6 columns in the current directory:
 - The input identifier
 - The Knowledge Network mapped identifier
 - The type of entity, 'Gene' or 'Property'
 - The official symbol or alias
 - The gene or property description
 - The gene biotype (e.g. protein coding)
 
Example output files, `sample_genes.node_map.txt` and `sample_props.node_map.txt`, can be found in this repository.

#### Default Usage With Docker
With Docker installed and the file you wish to map `your_genes.txt` in the current directory, a simple command is needed: 

    docker run --rm -w=`pwd` -v `pwd`:`pwd` knoweng/kn_mapper:latest \
        /home/src/kn_mapper.py your_genes.txt

You'll then see a map file, `your_genes.node_map.txt`, in the current directory. The `-w` sets the working directory for the container and the `-v` is used to volume mount the current directory to the container.

#### Parameters
The usage of the main function in this repo is: 

    kn_mapper.py [-h] [-rh REDIS_HOST] [-rp REDIS_PORT] [-rps REDIS_PASS]
                 [-of OUTFILE] [-sh SOURCE_HINT] [-t TAXON]
                 infile

If you want to modify the default parameters of kn_mapper.py, they include:

**-arg**|**--argument**  |**Description**|**Default**
--------|----------------|-----|-----
n/a     |infile          |path to the file with identifiers to be mapped|*required*
-rh     |\-\-redis\_host |address of Redis database|'knowredis.knoweng.org'
-rp     |\-\-redis\_port |port for Redis database|'6379'
-rps    |\-\-redis\_pass |password for Redis database|'KnowEnG'
-of     |\-\-outfile     |if specified, path to output file| 
-sh     |\-\-source\_hint|if specified, ID source database to resolve ambiguities| 
-t      |\-\-taxon       |taxon id of species for all gene names|'9606'

To find the list of taxon identifiers supported by the current version of KnowEnG, please visit this [link](https://knoweng.org/kn-data-references/#kn_contents_by_species).

## Alternative Usages
#### With a CWL runner tool

A sample job parameters file for running a kn_mapper job with a CWL tool runner is provided, `kn_mapper.job.yml`: 

    infile:
      class: File
      location: sample_genes.txt
    redis_host: knowredis.knoweng.org
    redis_port: 6379
    taxon: 9606

This template can be modified as needed and passed with the kn_mapper CWL description, `kn_mapper.cwl`, for execution with a CWL runner tool.

#### Run without Docker
You can also run the tool directly without docker:

    git clone https://github.com/KnowEnG/KN_Mapper.git
    cd KN_Mapper
    src/kn_mapper.py [path_to_input_file]


#### Building Docker Image Manually

Normally you would use the `knoweng/kn_mapper:latest` build image tag.  But if you need to build the image manually you would execute:

    git clone https://github.com/KnowEnG/KN_Mapper.git
    cd KN_Mapper
    docker build -t kn_mapper .


## Setting Up a Copy of the Redis Database

To set up your own copy of the redis database, you can grab the appropriate Redis database dump and then start up a Redis instance with it.  For example, with Docker:

    KNNET='20rep-1706'
    mkdir redis-$KNNET-6379
    aws s3 cp s3://KnowNets/KN-$KNNET/redis-KN-$KNNET.dump redis-$KNNET-6379/dump.rdb --region us-east-1
    # turn on redis
    docker run -d --restart=always --name kn_redis-$KNNET-6379 -p 6379:6379 \
        -v `pwd`/redis-$KNNET-6379:/data redis redis-server --requirepass KnowEnG
