# Pipelines for Document Processing
We implemented a pipeline for the PubPharm MEDLINE collection and for the [ZB MED preview's COVID-19 pre-prints](http://preview.zbmed.de). 
The scripts are located in [scripts](scripts/).

Add the +x flag to the scripts first:
```
chmod +x ~/NarrativeAnnotation/scripts/*.bs
```


The [MEDLINE script](scripts/process_pubmed_updates_for_service.bs) downloads MEDLINE metadata updates from the official NLM API.
Metadata is then inserted into our database.
After that, the script downloads new documents plus annotations from the [PubTator Central](https://www.ncbi.nlm.nih.gov/research/pubtator/) service.
Documents are load, tagged, classified and statements are extracted from them. 

```
bash ~/NarrativeAnnotation/scripts/process_pubmed_updates_for_service.bs
```


We implemented a similar [script for the ZB MED pre-prints](scripts/process_zbmed_for_service.bs). 
New pre-prints are crawled, transformed, loaded, tagged, classified and statements are extracted from them.


```
bash ~/NarrativeAnnotation/scripts/process_zbmed_for_service.bs
```


Extractions are not cleaned by the previous scripts. 
We implemented a script to:
- canonicalize the extractions
- apply the pharmaceutical cleaning logic
- apply additional SQL cleaning statements.

Note that you may adjust the script to enter your Postgres DB credentials. 

The [cleaning script](scripts/process_clean_extractions.bs) can be executed via:
```
bash ~/NarrativeAnnotation/scripts/Fprocess_clean_extractions.bs
```