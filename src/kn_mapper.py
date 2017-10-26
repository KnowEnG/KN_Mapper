#!/usr/bin/env python3

"""Utiliites for interacting with the KnowEnG Redis db through python.

Contains module functions::

    main_parse_args()
    get_database(args=None)
    get_node_info(rdb, fk_array, ntype, hint, taxid):
    conv_gene(rdb, fk_array, hint, taxid):
    node_desc(rdb, stable_array):

"""
import redis
import os
from argparse import ArgumentParser
import csv

DEFAULT_REDIS_URL = 'knowredis.knoweng.org'
DEFAULT_REDIS_PORT = '6379'
DEFAULT_REDIS_PASS = 'KnowEnG'
DEFAULT_HINT = None
DEFAULT_TAXON = 9606

def main_parse_args():
    """Processes command line arguments.

    Expects one positional argument (infile) and number of optional
    arguments. If arguments are missing, supplies default values.

.. csv-table::
    :header: parameter,argument,flag,description
    :widths: 4,2,2,12
    :delim: |

    --redis_host	|str	|-rh 	|url of Redis db
    --redis_port	|str	|-rp 	|port for Redis db
    --redis_pass	|str	|-rps	|password for Redis db

    Returns:
        Namespace: args as populated namespace
    """
    parser = ArgumentParser()
    parser.add_argument('infile', help='path to the file to be mapped.It should\
                        contain one identifer on each line.')
    parser.add_argument('-rh', '--redis_host', default=DEFAULT_REDIS_URL,
                        help='url of Redis db')
    parser.add_argument('-rp', '--redis_port', default=DEFAULT_REDIS_PORT,
                        help='port for Redis db')
    parser.add_argument('-rps', '--redis_pass', default=DEFAULT_REDIS_PASS,
                        help='password for Redis db')
    parser.add_argument('-of', '--outfile', default=None,
                        help='path to the output file')
    parser.add_argument('-sh', '--source_hint', help='suggestion for ID source \
                        database used to resolve ambiguities in mapping',
                        default=DEFAULT_HINT)
    parser.add_argument('-t', '--taxon', help='taxon id of species of all gene \
                        names', default=DEFAULT_TAXON)
    myargs = parser.parse_args()
    return myargs

def get_database(redis_host, redis_port, redis_pass):
    """Returns a Redis database connection.

    This returns a Redis database connection access to its functions if the
    module is imported.

    Args:
        args (Namespace): args as populated namespace or 'None' for defaults
    Returns:
        StrictRedis: a redis connection object
    """
    return redis.StrictRedis(host=redis_host, port=redis_port,
                             password=redis_pass)


def get_node_info(rdb, fk_array, ntype, hint, taxid):
    """Uses the redis database to convert a node alias to KN internal id

    Figures out the type of node for each id in fk_array and then returns
    all of the metadata associated or unmapped-*

    Args:
        rdb (redis object): redis connection to the mapping db
        fk_array (list): the array of foreign gene identifers to be translated
        ntype (str): 'Gene' or 'Property' or None
        hint (str): a hint for conversion
        taxid (str): the species taxid, None if unknown

    Returns:
        list: list of lists containing 5 col info for each mapped gene
    """
    hint = None if hint == '' or hint is None else hint.upper()
    taxid = None if taxid == '' or taxid is None else str(taxid)
    if ntype == '':
        ntype = None

    if ntype is None:
        res_arr = rdb.mget(['::'.join(['stable', str(fk), 'type']) for fk in fk_array])
        fk_prop = [fk for fk, res in zip(fk_array, res_arr) if res is not None and res.decode() == 'Property']
        fk_gene = [fk for fk, res in zip(fk_array, res_arr) if res is not None and res.decode() == 'Gene']
        if len(fk_prop) > 0 and len(fk_gene) > 0:
            raise ValueError("Mixture of property and gene nodes.")
        ntype = 'Property' if len(fk_prop) > 0 else 'Gene'

    if ntype == "Gene":
        stable_array = conv_gene(rdb, fk_array, hint, taxid)
    elif ntype == "Property":
        stable_array = fk_array
    else:
        raise ValueError("Invalid ntype")

    return list(zip(fk_array, *node_desc(rdb, stable_array)))


def conv_gene(rdb, fk_array, hint, taxid):
    """Uses the redis database to convert a gene to ensembl stable id

    This checks first if there is a unique name for the provided foreign key.
    If not it uses the hint and taxid to try and filter the foreign key
    possiblities to find a matching stable id.

    Args:
        rdb (redis object): redis connection to the mapping db
        fk_array (list): the foreign gene identifers to be translated
        hint (str): a hint for conversion
        taxid (str): the species taxid, 'unknown' if unknown

    Returns:
        str: result of searching for gene in redis DB
    """
    hint = None if hint == '' or hint is None else hint.upper()
    taxid = None if taxid == '' or taxid is None else str(taxid)

    #use ensembl internal uniprot mappings
    if hint == 'UNIPROT' or hint == 'UNIPROTKB':
        hint = 'UNIPROT_GN'

    ret_stable = ['unmapped-none'] * len(fk_array)

    def replace_none(ret_st, pattern):
        """Search redis for genes that still are unmapped
        """
        curr_none = [i for i in range(len(fk_array)) if ret_st[i] == 'unmapped-none']
        if curr_none:
            vals_array = rdb.mget([pattern.format(str(fk_array[i]).upper(), taxid, hint) for i in curr_none])
            for i, val in zip(curr_none, vals_array):
                if val is None: continue
                ret_st[i] = val.decode()

    if hint is not None and taxid is not None:
        replace_none(ret_stable, 'triplet::{0}::{1}::{2}')
    if taxid is not None:
        replace_none(ret_stable, 'taxon::{0}::{1}')
    if hint is not None:
        replace_none(ret_stable, 'hint::{0}::{2}')
    if taxid is None:
        replace_none(ret_stable, 'unique::{0}')
    return ret_stable


def node_desc(rdb, stable_array):
    """Uses the redis database to find metadata about node given its stable id

    Return all metadata for each element of stable_array

    Args:
        rdb (redis object): redis connection to the mapping db
        stable_array (str): the array of stable identifers to be searched

    Returns:
        list: list of lists containing 4 col info for each mapped node
    """
    ret_type = ["None"] * len(stable_array)
    ret_alias = list(stable_array)
    ret_desc = list(stable_array)
    st_map_idxs = [idx for idx, st in enumerate(stable_array) if not st.startswith('unmapped')]
    if st_map_idxs:
        vals_array = rdb.mget(['::'.join(['stable', stable_array[i], 'type']) for i in st_map_idxs])
        for i, val in zip(st_map_idxs, vals_array):
            if val is None: continue
            ret_type[i] = val.decode()
        vals_array = rdb.mget(['::'.join(['stable', stable_array[i], 'alias']) for i in st_map_idxs])
        for i, val in zip(st_map_idxs, vals_array):
            if val is None: continue
            ret_alias[i] = val.decode()
        vals_array = rdb.mget(['::'.join(['stable', stable_array[i], 'desc']) for i in st_map_idxs])
        for i, val in zip(st_map_idxs, vals_array):
            if val is None: continue
            ret_desc[i] = val.decode()
    return stable_array, ret_type, ret_alias, ret_desc


if __name__ == "__main__":

    args = main_parse_args()
    rdb = get_database(args.redis_host, args.redis_port, args.redis_pass)
    outfile = args.outfile
    if args.outfile is None:
        outfile = os.path.splitext(os.path.basename(args.infile))[0] + '.node_map.txt'
    with open(args.infile, 'r') as infile, \
        open(outfile, 'w') as n_map:
        reader = csv.reader(infile, delimiter='\t')
        writer = csv.writer(n_map, delimiter='\t', lineterminator='\n')
        mapped = get_node_info(rdb, [line[0] if len(line) > 0 else '' for line in reader],
                               None, args.source_hint, args.taxon)
        writer.writerows(mapped)

