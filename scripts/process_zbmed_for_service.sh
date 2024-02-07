#!/bin/bash

# load the db password
source .secret
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


DATA_PATH="/data/FID_Pharmazie_Services/narrative_data_update/zbmed/"

mkdir -p $DATA_PATH

ZBMED_JSON="$DATA_PATH"zbmed_updates.json
ZBMED_PUBTATOR="$DATA_PATH"zbmed.json
UPDATED_IDS="$DATA_PATH"updated_ids.txt

if [ "$(id -u)" == 0 ]; then
  TAG_CLEANING_SQL=/root/NarrativeAnnotation/sql/clean_tags.sql
  echo "root"
fi
if [ "$(id -u)" -ne 0 ]; then
  TAG_CLEANING_SQL=/home/$USER/NarrativeAnnotation/sql/clean_tags.sql
  echo "not root"
fi

## Load everything
# curl 'https://preview.zbmed.de/api/documents/' -X 'POST' -H 'Content-Type: application/json' -H 'Accept: application/json' --data-binary '{"size":40000,"from":0,"query":{"bool":{"must":[{"range":{"date":{"gte":"2019-12-01||/M","lt":"2021-12-18"}}}]}},"sort":[{"_score":{"order":"asc"}}],"track_total_hits":true}' >  $ZBMED_JSON

# First curl the updates since 01.12.2023
curl 'https://preview.zbmed.de/api/documents/' -X 'POST' -H 'Content-Type: application/json' -H 'Accept: application/json' --data-binary '{"size":40000,"from":0,"query":{"bool":{"must":[{"range":{"date":{"gte":"2023-12-01||/M"}}}]}},"sort":[{"_score":{"order":"asc"}}],"track_total_hits":true}' > $ZBMED_JSON
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Load everything
python3 ~/NarrativeAnnotation/src/narrant/document/load_zbmed_json.py $ZBMED_JSON -c ZBMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Next, tag the documents with our PharmDictTagger
python3 ~/NarrativeAnnotation/src/narrant/entitylinking/dictpreprocess.py -c ZBMed --skip-load --workers 5
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Execute Cleaning Rules for Tagging
echo 'cleaning Tag table with hand-written rules'
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=mininguser password=$PSQLPW" -f $TAG_CLEANING_SQL
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


# Perform classification
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py -c ZBMed -r ~/NarrativeAnnotation/resources/classification/pharmaceutical_classification_rules.txt --cls Pharmaceutical -w 15 --skip-load
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py -c ZBMed -r ~/NarrativeAnnotation/resources/classification/plant_specific_rules.txt --cls PlantSpecific -w 15 --skip-load
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/src/narrant/classification/apply_svm.py -c ZBMed /data/FID_Pharmazie_Services/narrative_data_update/pharmaceutical_technology_articles_svm.pkl --cls PharmaceuticalTechnology --workers 2
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


# Export the document content
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/document/export.py -d $ZBMED_PUBTATOR --collection ZBMed --format json
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Run GNormPlus
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/biomedical_entity_linking.py $ZBMED_PUBTATOR -c ZBMed --skip-load --workers 1 --gnormplus
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Do the statement extraction for all ZBMed documents via our Pipeline
python3 ~/NarrativeAnnotation/src/narrant/extraction/pharmaceutical_pipeline.py -c ZBMed -et PathIE --workers 2 --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi
