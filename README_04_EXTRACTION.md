# Pharmaceutical Extraction
The extraction procedure is based on our toolbox extraction methods.
However, we require an additional logic to filter gene ids for the extraction.
That is why we have a pharmaceutical version. 

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

The word embedding must be downloaded


```
wget https://ftp.ncbi.nlm.nih.gov/pub/lu/Suppl/BioSentVec/BioWordVec_PubMed_MIMICIII_d200.bin 
```

```

# Do the canonicalizing step
python3 ~NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/cleaning/canonicalize_predicates.py \
    --word2vec_model /data/workingdir/BioWordVec_PubMed_MIMICIII_d200.bin 
    --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json 
    --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID


```


## Apply Pharmaceutical Cleaning Logic


Apply the rules:
```
python3 ~/NarrativeAnnotation/src/narrant/cleaning/pharmaceutical_rules.py --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID
```

Execute Cleaning Rules for Predications
```
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=USER password=PW" -f home/pubpharm/NarrativeAnnotation/sql/clean_predication.sql
```