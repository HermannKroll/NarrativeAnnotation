# Pipelines for Document Processing
We implemented a pipeline for the PubPharm MEDLINE collection and for the [ZB MED preview's COVID-19 pre-prints](http://preview.zbmed.de). 
The scripts are located in [scripts](scripts/).

Add the +x flag to the scripts first:
```
chmod +x ~/NarrativeAnnotation/scripts/*.sh
```

# Adjust the working directory path
Open all scripts, adjust the paths and adjust the password of the database user:
- adjust data path
- adjust SQL paths

# Create env file
Create an environment file to set DB password as an env variable.
```
cd ~/NarrativeAnnotation/scripts
nano secrets
```

Paste the following content and replace the password:
```
PSQLPW="EXAMPLE_PW"
```

# Required pipeline data:
We need two additional files:
- a biomedical word embedding
- a trained pharmaceutical technology SVM model

Data is transferred by hand. There is no public download of these models. 

# Setup
The scripts can process db changes automatically.
Therefore, we need to know the current starting point (last update).
Export the latest predication id to a .txt file:
```
bash ~/NarrativeAnnotation/scripts/export_highest_predication_id.sh
```
This step needs only to be done once. 


# Medline Script:


The [MEDLINE script](scripts/process_pubmed_updates_for_service.sh) downloads MEDLINE metadata updates from the official NLM API.
Metadata is then inserted into our database.
After that, the script downloads new documents plus annotations from the [PubTator Central](https://www.ncbi.nlm.nih.gov/research/pubtator/) service.
Documents are load, tagged, classified and statements are extracted from them. 

```
bash ~/NarrativeAnnotation/scripts/process_pubmed_updates_for_service.sh
```


# ZB MED Script

We implemented a similar [script for the ZB MED pre-prints](scripts/process_zbmed_for_service.sh). 
New pre-prints are crawled, transformed, loaded, tagged, classified and statements are extracted from them.


```
bash ~/NarrativeAnnotation/scripts/process_zbmed_for_service.sh
```

# Clean Data


Extractions are not cleaned by the previous scripts. 
We implemented a script to:
- canonicalize the extractions
- apply the pharmaceutical cleaning logic
- apply additional SQL cleaning statements.

Note that you may adjust the script to enter your Postgres DB credentials. 

The [cleaning script](scripts/process_clean_extractions.sh) can be executed via:
```
bash ~/NarrativeAnnotation/scripts/process_clean_extractions.sh
```