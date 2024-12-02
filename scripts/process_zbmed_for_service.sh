#!/bin/bash


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


bash ~/NarrativeAnnotation/scripts/process_document_collection.sh "$ZBMED_JSON" "ZBMed"
if [[ $? != 0 ]]; then
      echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

