# Pharmaceutical Extraction
The extraction procedure is based on our toolbox extraction methods.
However, we require an additional logic to filter gene ids for the extraction.
That is why we have a pharmaceutical version. 

For the extraction part, additional indexes are required.
```
python3 ~/NarrativeAnnotation/src/narrant/build_all_indexes.py
```


Run the pharmaceutical extraction pipeline via:
```
python3 ~/NarrativeAnnotation/src/narrant/extraction/pharmaceutical_pipeline.py --idfile $UPDATED_IDS \ 
    -c PubMed -et PathIE --workers 2 --bs 50000 \
    --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json
```

Arguments:
- **--idfile** specifies 
- **-c**: the collection
- **-et**: the extraction method. We always use PathIE.
- **--workers**: number of parallel works
- **-bs**: batch size (how many documents should be processed in one batch)
- **--relation_vocab** the relation vocabulary for additional keywords used in the extraction method (e.g., signaling words like therapy).


## Canonicalize Verb Phrases
The previous procedure extracts noisy verb phrases from texts, e.g., predicates might be words like therapy and treat.
These noise phrases are not mapped to precise relations at the moment.
Therefore, we designed an canonicalization procedure which utilizes a biomedical word embedding.

Create a new directory to store the embedding:
```
mkdir ~/data/
cd ~/data/
```


The word embedding must be downloaded from an external source:
```
wget https://ftp.ncbi.nlm.nih.gov/pub/lu/Suppl/BioSentVec/BioWordVec_PubMed_MIMICIII_d200.bin 
```

Finally, the noise verb phrases in our database can be canonicalized via:
```
# Do the canonicalizing step
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/cleaning/canonicalize_predicates.py \
    --word2vec_model ~/data/BioWordVec_PubMed_MIMICIII_d200.bin \
    --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json \
    --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID
```

Arguments are:
- **word2vec_model** specifys the path to the biomedical word embedding
- **relation_vocab** specifys the path to our relation vocabulary (necessary to canonicalize the extractions)
- **predicate_id_minimum** is an optional argument to specify which predication ids should be updated.

The idea is that only documents are updated which are new since the last update.
Therefore, all predication entries are queried that have an id greater equal the minimum predication id.
This mode is way faster and less memory intensive than canonicalizing the whole table.


## Apply Pharmaceutical Cleaning Logic
Next, we have some special pharmaceutical rules. 
Please run:
```
python3 ~/NarrativeAnnotation/src/narrant/cleaning/pharmaceutical_rules.py --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID
```

Arguments are:
- **predicate_id_minimum** is an optional argument to specify which predication ids should be updated.

The idea is that only documents are updated which are new since the last update.
Therefore, all predication entries are queried that have an id greater equal the minimum predication id.
This mode is way faster and less memory intensive than apply rules to the the whole table.


Finally, we curate some extra cleaning rules formulated in SQL. 
Execute the following cleaning rules for the Predication table:
```
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=USER password=PW" -f ~/NarrativeAnnotation/sql/clean_predication.sql
```