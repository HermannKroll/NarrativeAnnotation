#!/bin/bash

DATA_PATH="/data/zbmed/"

ZBMED_JSON="$DATA_PATH"zbmed_updates.json
ZBMED_PUBTATOR="$DATA_PATH"zbmed.json
UPDATED_IDS="$DATA_PATH"updated_ids.txt

TAG_CLEANING_SQL=/home/"$USER"/NarrativeAnnotation/sql/clean_tags.sql


## Load everything
# curl 'https://preview.zbmed.de/api/documents/' -X 'POST' -H 'Content-Type: application/json' -H 'Accept: application/json' --data-binary '{"size":40000,"from":0,"query":{"bool":{"must":[{"range":{"date":{"gte":"2019-12-01||/M","lt":"2021-12-18"}}}]}},"sort":[{"_score":{"order":"asc"}}],"track_total_hits":true}' >  $ZBMED_JSON

# First curl the updates since 01.12.2023
curl 'https://preview.zbmed.de/api/documents/' -X 'POST' -H 'Content-Type: application/json' -H 'Accept: application/json' --data-binary '{"size":40000,"from":0,"query":{"bool":{"must":[{"range":{"date":{"gte":"2023-12-01||/M"}}}]}},"sort":[{"_score":{"order":"asc"}}],"track_total_hits":true}' > $ZBMED_JSON

# Load everything
python3 ~/NarrativeAnnotation/src/narrant/document/load_zbmed_json.py $ZBMED_JSON -c ZBMed

# Next, tag the documents with our PharmDictTagger
python3 ~/NarrativeAnnotation/src/narrant/preprocessing/dictpreprocess.py -c ZBMed --skip-load --workers 5

# Execute Cleaning Rules for Tagging
echo 'cleaning Tag table with hand-written rules'
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=mininguser password=F2M>FAJL2ptVm)W" -f $TAG_CLEANING_SQL

# Perform classification
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py -c ZBMed -r ~/NarrativeAnnotation/resources/classification/pharmaceutical_classification_rules.txt --cls Pharmaceutical -w 15 --skip-load
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py -c ZBMed -r ~/NarrativeAnnotation/resources/classification/plant_specific_rules.txt --cls PlantSpecific -w 15 --skip-load
python3 ~/NarrativeAnnotation/src/narrant/classification/apply_svm.py -c ZBMed ~/pharmaceutical_technology_articles_svm.pkl --cls PharmaceuticalTechnology --workers 2

# Export the document content
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/document/export.py -d $ZBMED_PUBTATOR --collection ZBMed --format json

# Run GNormPlus
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/biomedical_entity_linking.py $ZBMED_PUBTATOR -c ZBMed --skip-load --workers 1 --gnormplus

# Do the statement extraction for all ZBMed documents via our Pipeline
python3 ~/NarrativeAnnotation/src/narrant/extraction/pharmaceutical_pipeline.py -c ZBMed -et PathIE --workers 2 --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json

