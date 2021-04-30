
## Preprocessing
### Hardware Configuration
We recommend to have at least 32GB of RAM available. 
### Checkout or download the GitHub project
```
cd NarrativeAnnotation/
# Download important data
./download_data.sh
```
### Create a directory for the tagger tools
```
mkdir ~/tools
```
### Taggers
Download [GNormPlus](https://www.ncbi.nlm.nih.gov/research/bionlp/Tools/gnormplus/) and [TaggerOne](https://www.ncbi.nlm.nih.gov/research/bionlp/tools/taggerone/). Unzip both and move the directories into tools. 
```
tools/
  GNormPlusJava/
  TaggerOne-0.2.1/
```
Both tools require an Java installation. 

### Tagger Configuration
Configure the tagger locations for the project
```
cd projectroot/config/
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
  }
}
```
You can ignore the pmcid2pmid setting.

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
Install python >= 3.6. Decider whether you want to work with a global python version or with a conda environment (see [tutorial](https://towardsdatascience.com/getting-started-with-python-environments-using-conda-32e9f2779307))
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

### Tagging Documents
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

# Running the Annotators

## TaggerOne and GNormPlus
Finally we can start tagging our documents. Assume we have a test document test.pubtator.
```
cd ~/NarrativeAnnotation/
python3 narrant/preprocessing/preprocess.py ~/test.pubtator  --corpus test --tagger-one --gnormplus
```
The pipeline will invoke the taggers to tag the documents. The document corpus is *test*. 

--tagger-one means that TaggerOne will be used to annotate Chemicals and Diseases.

--gnormplus means that GNormPlus will be used to annotate Genes and Species.

The pipeline will work in a temporary directory and remove it if the task is completed. If you want to work in a specified directory, use
```
cd ~/NarrativeAnnotation/
python3 narrant/preprocessing/preprocess.py ~/test.pubtator --corpus test -t A --workdir temp/
```
The temporary created files as well as all logs won't be removed then. 

## Dictionary-based Taggers (Own Vocabularies)
You can invoke our own dictionary-based tagger pipeline via
```
cd ~/NarrativeAnnotation/
python3 narrant/preprocessing/dictpreprocess.py ~/test.pubtator  --corpus test
```
The pipeline annotates Diseases, Dosage Forms, Drugs, DrugBank Chemicals, Excipients, Methods, LebMethods and Plant Families.


You can specify a working directory and the number of parallel workers:
```
cd ~/NarrativeAnnotation/
python3 narrant/preprocessing/dictpreprocess.py ~/test.pubtator --corpus test --workdir test/ --workers 10
```


## Database scheme

![DB Scheme](dbschema.png)
created with app.quickdatabasediagrams.com
### Export XML UB
If you want to export in our specified XML format, use the following script. You need to create some indexes before you can use the xml export.
```
python3 narrant/entity/entitiyresolver.py
```
This might take a while and will build all required indexes. Then, you can export the documents
```
python3 narrant/backend/exports/xml_export.py
```
See help for parameter description. 
