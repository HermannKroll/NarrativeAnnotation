#!/bin/bash

# load the db password
source .secret
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi



DATA_PATH="/data/FID_Pharmazie_Services/narrative_data_update/pubmed/"

mkdir -p $DATA_PATH

PHARM_TECH_IDS="$DATA_PATH"/pharm_technology_ids.tsv
ALL_PUBTATOR_PMIDS="$DATA_PATH"pubtator_pmids_all.txt
PMIDS_IN_DB="$DATA_PATH"pmids_in_db.txt
IDS_TO_DOWNLOAD="$DATA_PATH"pubtator_pmids_to_download.txt
LITCOVID_ID_FILE="$DATA_PATH"litcovid_ids.tsv
LONGCOVID_ID_FILE="$DATA_PATH"long_covid_ids.tsv

UPDATES_PUBTATOR="$DATA_PATH"pubtator_updates.pubtator
UPDATED_IDS="$DATA_PATH"pharmaceutical_relevant_ids.txt

if [ "$(id -u)" == 0 ]; then
  TAG_CLEANING_SQL=/root/NarrativeAnnotation/sql/clean_tags.sql
  echo "root"
fi
if [ "$(id -u)" -ne 0 ]; then
  TAG_CLEANING_SQL=/home/$USER/NarrativeAnnotation/sql/clean_tags.sql
  echo "not root"
fi


MEDLINE_BASELINE="$DATA_PATH"baseline/
MEDLINE_UPDATES="$DATA_PATH"updates/


cd $PUBMED_ROOT
mkdir $MEDLINE_BASELINE
mkdir $MEDLINE_UPDATES


# First get all PubMed Pubtator PMIDs
wget https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral/AvailablePMIDsinPubTator.txt -O $ALL_PUBTATOR_PMIDS
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Export all known document ids from the database
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/backend/export_document_ids.py $PMIDS_IN_DB -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Compute the open ids (known PubTator ids but NOT in database)
python3 ~/NarrativeAnnotation/src/narrant/util/compute_id_file_diff.py $ALL_PUBTATOR_PMIDS $PMIDS_IN_DB $IDS_TO_DOWNLOAD
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Download all PubTator files + their annotations
python3 ~/NarrativeAnnotation/src/narrant/pubtator/download_pubtator_central_files.py $IDS_TO_DOWNLOAD $UPDATES_PUBTATOR
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Load all PubTator files to database
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/document/load_document.py $UPDATES_PUBTATOR -c PubMed --tagger-map ~/NarrativeAnnotation/resources/pubtator_central_taggermap.json
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Next, tag the documents with our PharmDictTagger
python3 ~/NarrativeAnnotation/src/narrant/entitylinking/dictpreprocess.py -i $UPDATES_PUBTATOR -c PubMed --skip-load --workers 2
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
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  -i $UPDATES_PUBTATOR -c PubMed -r ~/NarrativeAnnotation/resources/classification/pharmaceutical_classification_rules.txt --cls Pharmaceutical -w 15 --skip-load
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  -i $UPDATES_PUBTATOR -c PubMed -r ~/NarrativeAnnotation/resources/classification/plant_specific_rules.txt --cls PlantSpecific -w 15 --skip-load
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/src/narrant/classification/apply_svm.py -i $UPDATES_PUBTATOR -c PubMed /data/FID_Pharmazie_Services/narrative_data_update/pharmaceutical_technology_articles_svm.pkl --cls PharmaceuticalTechnology --workers 10
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Load Pharmaceutical Journals as Pharmaceutical Technology
python3 ~/NarrativeAnnotation/src/narrant/backend/export_article_ids_from_journals.py ~/NarrativeAnnotation/resources/classification/pharmaceutical_technology_journals.txt $PHARM_TECH_IDS -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py  $PHARM_TECH_IDS PharmaceuticalTechnology -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


# Load all LitCOVID + Long Covid classifications
wget https://www.ncbi.nlm.nih.gov/research/coronavirus-api/export/all/tsv -O $LITCOVID_ID_FILE
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

wget 'https://www.ncbi.nlm.nih.gov/research/coronavirus-api/export/tsv?text=e_condition%3ALongCovid&filters=%7B%7D' -O $LONGCOVID_ID_FILE
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py $LITCOVID_ID_FILE LitCovid -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py $LONGCOVID_ID_FILE LongCovid -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Finally, all files have been tagged
python3 ~/NarrativeAnnotation/src/narrant/analysis/export_relevant_pharmaceutical_documents.py $UPDATED_IDS -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Do the statement extraction via our Pipeline
python3 ~/NarrativeAnnotation/src/narrant/extraction/pharmaceutical_pipeline.py -bs 50000 --idfile $UPDATED_IDS -c PubMed -et PathIE --workers 10 --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


# Load the Metadata
# Donwload the latest medline via
# wget -m ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/ -P $MEDLINE_BASELINE
# Download the latest updates via
wget -m ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles -P $MEDLINE_UPDATES
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Load Updates
python3 ~/NarrativeAnnotation/src/narrant/document/load_pubmed_metadata.py $MEDLINE_UPDATES -c PubMed
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi
# Load Baseline
# python3 ~/NarrativeAnnotation/src/narrant/document/load_pubmed_metadata.py $MEDLINE_BASELINE -c PubMed
