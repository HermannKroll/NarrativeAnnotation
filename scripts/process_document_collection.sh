#!/bin/bash

# load the db password
source ~/NarrativeAnnotation/scripts/.secret
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

DOC_UPDATES=$1
COLLECTION=$2

if [ "$(id -u)" == 0 ]; then
  TAG_CLEANING_SQL=/root/NarrativeAnnotation/sql/clean_tags.sql
  echo "root"
fi
if [ "$(id -u)" -ne 0 ]; then
  TAG_CLEANING_SQL=/home/$USER/NarrativeAnnotation/sql/clean_tags.sql
  echo "not root"
fi



# Next, tag the documents with our PharmDictTagger
python3 ~/NarrativeAnnotation/src/narrant/entitylinking/dictpreprocess.py -i $DOC_UPDATES -c $COLLECTION --skip-load --workers 10
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Run GNormPlus
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/biomedical_entity_linking.py $DOC_UPDATES -c ZBMed --skip-load --workers 5 --gnormplus
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Some gene annotations are composed (e.g, id = 123;345) this ids need to be split into multiple tag entries
python3 ~/NarrativeAnnotation/src/narrant/cleaning/clean_tag_gene_ids.py
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
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  -i $DOC_UPDATES -c $COLLECTION -r ~/NarrativeAnnotation/resources/classification/pharmaceutical_classification_rules.txt --cls Pharmaceutical -w 15 --skip-load
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  -i $DOC_UPDATES -c $COLLECTION -r ~/NarrativeAnnotation/resources/classification/plant_specific_rules.txt --cls PlantSpecific -w 15 --skip-load
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/src/narrant/classification/apply_svm.py -i $DOC_UPDATES -c $COLLECTION /data/FID_Pharmazie_Services/narrative_data_update/pharmaceutical_technology_articles_svm.pkl --cls PharmaceuticalTechnology --workers 10
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


# Do the statement extraction via our Pipeline
python3 ~/NarrativeAnnotation/src/narrant/extraction/pharmaceutical_pipeline.py -bs 50000 -c $COLLECTION -et PathIE --workers 10 --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

