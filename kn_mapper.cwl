class: CommandLineTool
cwlVersion: v1.0
id: "kn_mapper"
label: "Knowledge Network Gene Mapper"
doc: "Maps gene identifiers in file to standardized entities in the Knowledge Network"

requirements:
  - class: DockerRequirement
    dockerPull: "quay.io/cblatti3/kn_mapper:0.1"
  - class: InlineJavascriptRequirement

hints:
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 1024 #"the process requires at least 1G of RAM
    outdirMin: 512000

inputs:
  infile:
    label: Input File
    doc: path to the file to be mapped. It should contain one identifer on each line.
    type: File
    inputBinding:
      position: 1
  redis_host:
    type: ["null", string]
    default: knowredis.knoweng.org
    label: RedisDB URL
    doc: url of Redis db
    inputBinding:
      prefix: --redis_host
  redis_port:
    type: ["null", int]
    default: 6379
    label: RedisDB Port
    doc: port for Redis db
    inputBinding:
      prefix: --redis_port
  redis_pass:
    type: ["null", string]
    default: KnowEnG
    label: RedisDB AuthStr
    doc: password for Redis db
    inputBinding:
      prefix: --redis_pass
  taxon:
    type: ["null", int]
    default: 9606
    label: Species TaxonID
    doc: taxon id of species of all gene names
    inputBinding:
      prefix: --taxon
  source_hint:
    type: ["null", string]
    label: ID Source Hint
    doc: suggestion for ID source database used to resolve ambiguities in mapping
    inputBinding:
      prefix: --source_hint

baseCommand: ['/home/src/kn_mapper.py']

outputs:
  output_file:
    label: Map File
    doc: 4 column format for mapped entities [orig_id, KN_id, type, alias, desc]
    outputBinding:
      glob: "*.node_map.txt"
    type: File
