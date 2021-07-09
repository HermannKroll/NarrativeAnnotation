# General 
This repository contains methods to annotate entities in document text. We build the pipeline upon a relational database structure, i.e., 
all relevant information will be stored in the database. For example, annotating documents will first insert the documents into the database and then insert the 
produced annotations as well. After the annotation is completed, the annotation can be exported.

We distinguish documents by their id and their collection. We assume documents to have an unique integer id within a document collection. 
For example, the document id *123* is must refer to a unique id within the collection *Test*.


Some general remarks:
- document ids must be integer and must be unique within a document collection
- a document collection can be an arbitrary string
- documents won't be tagged twice. Our pipeline checks whether the documents were tagged for the given entity types before. Only new documents will be tagged.  
- documents must be in the PubTator format
- documents that do not meet the above constraint may be transformed first. See the src/narrant/pubtator/translation for good examples
- there is an additional table (DocumentTranslation) in which such a translation could be stored
- Documents won't be inserted twice. There is a global setting that duplicated tuples are ignored when inserted in the database.

## Supported Document Formats

Our Pipeline supports 2 input formats (Pubtator, json) and 3 export formats (pubtator, json, xml). The import formats are explained below. For the xml export please refer to the export section at the end of this readme.

### json
Here is an example of our json format:
```
[
  {
  "id": 12098649,
  "title": "Lack of association between estrogen receptor 1 gene polymorphisms and multiple sclerosis in southern Italy in humans.",
  "abstract": "Estrogen receptor 1 gene polymorphisms (ESR1) have been found to be associated with multiple sclerosis (MS) in both Japanese and Finnish populations. We investigated the association between ESR1 polymorphisms (PvuII and XbaI) and MS in a study of 132 MS patients and 129 controls from the same geographic background (southern Italy). Allelic and genotypic frequencies were not different between MS patients and population controls for either the PvuII or XbaI polymorphism. This result suggests that the association between a given disease and a genomic characteristic must be confirmed by separate investigations in different populations.",
  "tags": [
    {
      "id": "2099",
      "mention": "estrogen receptor 1",
      "start": 28, // Python: (title + " " + abstract)[start:end]==mention,
      "end": 47,
      "type": "Gene"
    }
    //...
  ]
  },
  //...
]
```
The outmost array brackets `[]` can be omitted if only a single json document should be contained within the file.


### Pubtator
We assume each document to have a document id, a document collection, a title and an abstract. Document ids must be unique with a document collection. Our pipeline expects documents to be in the [PubTator format](https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/tutorial/index.html). 
```
document_id|t|title text here
document_id|a|abstract text here

```
ATTENTION: the PubTator file must end with two *\n* characters. 
The document id must be an integer. Title and abstract can include special characters - the texts will be sanitized in our pipeline. 
If you want to tag several documents, you can choose from two options:
1. Create a PubTator file for each document and put them into a directory
2. Create a single PubTator file with several documents
```
document_id_1|t|title text here
document_id_1|a|abstract text here

document_id_2|t|title text here
document_id_2|a|abstract text here

document_id_3|t|title text here
document_id_3|a|abstract text here

```
The files are separated by two new line characters *\\n*. ATTENTION: the PubTator file must end with two *\\n* characters. 

## Database Schema

![DB Scheme](dbschema.png)
created with app.quickdatabasediagrams.com


# Preprocessing
### Hardware Configuration
We recommend having at least 32GB of RAM available. 
### Checkout or download the GitHub project

Then,additional data must be downloaded. Switch to the NarrativeAnnotation directory and execute the bash script_
```
cd NarrativeAnnotation/
./download_data.sh
```

### Database Setup
1. Setup a PostgresDB environment (see [official instructions](https://www.postgresql.org)). Tagging results, documents and more will be stored in this relational database. 
2. Create a new database and user for the preprocessing pipeline, e.g. *taggingdb* and *tagginguser*

### Database configuration
Setup the database configuration in the project
```
cd NarrativeAnnotation/config/
cp backend.prod.json backend.json
nano backend.json
```
Enter your database credentials, e.g.:
```
{
  "POSTGRES_DB": "example",
  "POSTGRES_HOST": "127.0.0.1",
  "POSTGRES_PORT": "5432",
  "POSTGRES_USER": "user",
  "POSTGRES_PW": "pw",
  "POSTGRES_SCHEMA": "public"
}
```

### Install Python
Install python >= 3.7. Decider whether you want to work with a global python version or with a conda environment (see [tutorial](https://towardsdatascience.com/getting-started-with-python-environments-using-conda-32e9f2779307))
### Dependencies
Install all packages from requirements.txt
```
pip3 install -r requirements.txt
```

### Python Path
You need to setup the python path. This procedure must be repeated every time you create a new shell. You can add the path to your bash defaults.
```
export PYTHONPATH=/home/kroll/NarrativeAnnotation/
```


# Running the Annotators
In this section, we briefly describe how to user our pipeline. For the examples below, we suppose you to be in the correct directory. So,
```
cd ~/NarrativeAnnotation/
```
The idea of our pipeline is based on entity types. For example, if a user want to annotate drugs in text, then the corresponding annotation tool will be invoked. 
Hence, the user could specifiy which entity types she wants to annotate in texts.

## Annotation Data (Tags)
The tagging pipeline produces tags. A tag represents an annotation and consists of a:
- document id (int)
- document collection (string)
- start position in text (int)
- end position in text (int)
- entity str (the annotated text sequence, string)  
- entity id (string)
- entity type (string)

We provide a total of three scripts for generating annotations:
- Two for dictionary-based Taggers
  - Either using our own vocabulary
  - or using a custom vocabulary read from a .tsv file
- One for Third-Party tools (Taggerone, GNormPlus)

The usage of the pipelines will be explained in the following.


## Dictionary-based Taggers (Our Vocabularies)
The documents must be in the database for annotation purposes. If you call an annotation script, the documents will automatically be inserted. 
You can invoke our own dictionary-based tagger pipeline via
```
python3 src/narrant/preprocessing/dictpreprocess.py test.pubtator --corpus test
```
This call will invoke the pipeline to annoate all known entity types.
The pipeline annotates Diseases, Dosage Forms, Drugs, DrugBank Chemicals, Excipients, Methods, LebMethods and Plant Families.
The first run will build all necessary indexes that will speed up further runs. So, the first run may take a bit.


You can may also speedup the tagging process. You invoke multiple parallel workers. 
The number of parallel workers can be specified as follows:
```
python3 src/narrant/preprocessing/dictpreprocess.py test.pubtator --corpus test --workers 10
```

If you are certain that all documents are already in the database, you may skip the loading phase by:
```
python3 src/narrant/preprocessing/dictpreprocess.py test.pubtator --corpus test --skip-load
```


The pipeline will work in a temporary directory (random directory in /tmp/) and remove it if the task is completed. If you want to work in a specified directory, use
```
python3 src/narrant/preprocessing/dictpreprocess.py test.pubtator --corpus test --workdir temp/
```
The temporary created files as well as all logs won't be removed then. 

It is to be noted that the dictionary-based pipelines solely create the tags and insert them into the database. If the tags are needed in a file format, an export has to be executed afterwards.

## Dictionary-Based Taggers (Custom Vocabulary)
This pipeline offers the chance to load a custom vocabulary from a tsv file.

### Usage
```
usage: vocab_dictpreprocess.py [-h] -c COLLECTION -v--vocabulary V__VOCABULARY
                               [--config CONFIG] [--loglevel LOGLEVEL]
                               [--workdir WORKDIR] [--skip-load] [-w WORKERS]
                               [-y]
                               IN_DIR
```
#### Example
```
src/narrant/preprocessing/vocab_dictpreprocess.py input_directory/ -c test -v test_vocabulary.tsv
```
This pipeline supports the same options as the dictpreprocess pipeline discussed above. 

However, this script also requires a vocabulary file specified with the `-v` tag.
It's format looks like this:
```
id	enttype	heading	synonyms
<entity identifier> <entity type> <entity main name> <synonyms to be tagged, separated by semicolons (;)>
<entity identifier> <entity type> <entity main name> <synonyms to be tagged, separated by semicolons (;)>
...
```

For more clarity, see this example bewlow:
```
id	enttype	heading	synonyms
D063465	DosageForm	Cream	Lotion;Gel-cream;gel cream
D053770	DosageForm	Nano wires	Nano wire;Nano-wires;Nano-wire
CHEMBL1064  Drug  Simvastatin Simvastatinum;Simvastatina
...
```


## TaggerOne and GNormPlus (ThirdParty)
In addition to our own annotation tools, we build support for two frequently used biomedical tools. 
TaggerOne supports the annotation of Chemicals and Diseases.
GNormPlus supports the annotation of Genes and Species.
### Create a directory for the tagger tools
```
mkdir ~/tools
```
### Third-Party Taggers
Download [GNormPlus](https://www.ncbi.nlm.nih.gov/research/bionlp/Tools/gnormplus/) and [TaggerOne](https://www.ncbi.nlm.nih.gov/research/bionlp/tools/taggerone/). Unzip both and move the directories into tools. 
```
tools/
  GNormPlusJava/
  TaggerOne-0.2.1/
```
Both tools require a Java installation. To use TaggerOne, see its readme file. Some models must be build manually.

### Tagger Configuration
Configure the tagger locations for the project
```
cd NarrativeAnnotation/config/
cp preprocess.prod.json preprocess.json
nano preprocess.json
```
Enter your GNormPlus and TaggerOne root paths
```
{
  "taggerOne": {
    "root": "/home/kroll/tools/tagger/TaggerOne-0.2.1",
    "model": "models/model_BC5CDRJ_011.bin",
    "batchSize": 10000,
    "timeout": 15,
    "max_retries": 1
  },
  "gnormPlus": {
    "root": "/home/kroll/tools/tagger/GNormPlusJava",
    "javaArgs": "-Xmx100G -Xms30G"
  },
  "dict": {
    "max_words": 5,
    "check_abbreviation": "true",
    "custom_abbreviations": "true",
    "min_full_tag_len": 5
  },
  "drug": {
    "check_products" : 0,
    "max_per_product": 2,
    "min_name_length": 3,
    "ignore_excipient_terms": 1
  }
}
```
You can ignore the other parameters for now.

### Run the ThirdParty Annotators
You may annotate documents with TaggerOne and GNormPlus. Assume we have a test document test.pubtator.
```
python3 src/narrant/preprocessing/preprocess.py test.pubtator --corpus test --tagger-one --gnormplus
```
The pipeline will invoke the taggers to tag the documents. The document corpus is *test*.
The tools can be invoked by:
- tagger-one means that TaggerOne will be used to annotate Chemicals and Diseases.
- gnormplus means that GNormPlus will be used to annotate Genes and Species.

The pipeline will work in a temporary directory and remove it if the task is completed. If you want to work in a specified directory, use
```
python3 src/narrant/preprocessing/preprocess.py test.pubtator --corpus test --workdir temp/ --gnormplus --tagger-one
```
The temporary created files as well as all logs won't be removed then.

# Export

There are two different export scripts:
- One for export in json or pubtator format
- One for export in xml format

### Export JSON / Pubtator
#### Usage: 
```
usage: export.py [-h] [--ids [DOC_ID [DOC_ID ...]]] [--idfile IDFILE]
                 [-c COLLECTION] [-d]
                 [-t {DF,DR,DC,E,PF,C,MU,G,S,D,V,CL,M,LM,A,DA} [{DF,DR,DC,E,PF,C,MU,G,S,D,V,CL,M,LM,A,DA} ...]]
                 [--format {json,pubtator}] [--sqllog]
                 output

positional arguments:
  output

optional arguments:
  -h, --help            show this help message and exit
  --ids [DOC_ID [DOC_ID ...]]
  --idfile IDFILE       file containing document ids (one id per line)
  -c COLLECTION, --collection COLLECTION
                        Collection(s)
  -d, --document        Export content of document
  -t {DF,DR,DC,E,PF,C,MU,G,S,D,V,CL,M,LM,A,DA} [{DF,DR,DC,E,PF,C,MU,G,S,D,V,CL,M,LM,A,DA} ...], --tag {DF,DR,DC,E,PF,C,MU,G,S,D,V,CL,M,LM,A,DA} [{DF,DR,DC,E,PF,C,MU,G,S,D,V,CL,M,LM,A,DA} ...]
  --format {json,pubtator}, -f {json,pubtator}
                        export format
  --sqllog              logs sql commands

```
#### Example
```
python3 src/narrant/backend/export.py -h --ids 1 2 3 -c TEST -d -t DF DR C --format json output_file
```
This will export the titles, abstracts and tags for documents 1,2,3 in collection Test to outptu_file in the json format.

### Export XML UB
If you want to export in our specified XML format, use the following script. You need to create some indexes before you can use the xml export.
The script will ask you, if your database connection is configured properly. 
So, first run:
```
python3 src/narrant/build_all_indexes.py
```
...and enter yes if the correct database connection is selected.
This might take a while and will build all required indexes. 
Attention: indexes for genes and species will only be build for those tag ids that have been annotated so far. If you annotate mor documents, you must rebuild the indexes. 


Finally, you can export the documents
```
python3 src/narrant/backend/exports/xml_export.py output_dir -c COLLECTION_NAME
```
See help for parameter description. The output format looks like: document_id.xml and the content:



```
<?xml version="1.0" ?>
<document>
   <tag source="NCBI Gene">eukaryotic translation initiation factor 2 alpha kinase 2</tag>
   <tag source="NCBI Gene">Atf4</tag>
   <tag source="NCBI Gene">DNA damage inducible transcript 3</tag>
   <tag source="NCBI Gene">DDIT3</tag>
   <tag source="NCBI Gene">eukaryotic translation initiation factor 2 alpha kinase 3</tag>
   <tag source="NCBI Gene">EIF2AK3</tag>
   <tag source="DrugBank">Toyocamycin</tag>
   <tag source="NCBI Taxonomy">house mouse</tag>
   <tag source="NCBI Taxonomy">Mus musculus</tag>
   <tag source="MeSH">Wounds and Injuries</tag>
   <tag source="MeSH">Death</tag>
</document>

```
