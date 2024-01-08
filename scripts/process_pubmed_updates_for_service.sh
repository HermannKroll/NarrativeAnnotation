#!/bin/bash

DATA_PATH="/data/pubmed/"

PHARM_TECH_IDS="$DATA_PATH"/pharm_technology_ids.tsv
ALL_PUBTATOR_PMIDS="$DATA_PATH"pubtator_pmids_all.txt
PMIDS_IN_DB="$DATA_PATH"pmids_in_db.txt
IDS_TO_DOWNLOAD="$DATA_PATH"pubtator_pmids_to_download.txt
LITCOVID_ID_FILE="$DATA_PATH"litcovid_ids.tsv
LONGCOVID_ID_FILE="$DATA_PATH"long_covid_ids.tsv

UPDATES_PUBTATOR="$DATA_PATH"pubtator_updates.pubtator
UPDATED_IDS="$DATA_PATH"pharmaceutical_relevant_ids.txt

TAG_CLEANING_SQL=/home/"$USER"/NarrativeAnnotation/sql/clean_tags.sql

MEDLINE_BASELINE="$DATA_PATH"baseline/
MEDLINE_UPDATES="$DATA_PATH"updates/


cd $PUBMED_ROOT
mkdir $MEDLINE_BASELINE
mkdir $MEDLINE_UPDATES

# Load the Metadata
# Donwload the latest medline via
# wget -m ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/ -P $MEDLINE_BASELINE
# Download the latest updates via
wget -m ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles -P $MEDLINE_UPDATES

# Load Updates
python3 ~/NarrativeAnnotation/src/narrant/document/load_pubmed_metadata.py $MEDLINE_UPDATES -c PubMed
# Load Baseline
# python3 ~/NarrativeAnnotation/src/narrant/document/load_pubmed_metadata.py $MEDLINE_BASELINE -c PubMed




# First get all PubMed Pubtator PMIDs
wget https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral/AvailablePMIDsinPubTator.txt -O $ALL_PUBTATOR_PMIDS

# Export all known document ids from the database
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/backend/export_document_ids.py $PMIDS_IN_DB -c PubMed

# Compute the open ids (known PubTator ids but NOT in database)
python3 ~/NarrativeAnnotation/src/narrant/util/compute_id_file_diff.py $ALL_PUBTATOR_PMIDS $PMIDS_IN_DB $IDS_TO_DOWNLOAD

# Download all PubTator files + their annotations
python3 ~/NarrativeAnnotation/src/narrant/pubtator/download_pubtator_central_files.py $IDS_TO_DOWNLOAD $UPDATES_PUBTATOR

# Load all PubTator files to database
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/document/load_document.py $UPDATES_PUBTATOR -c PubMed --tagger-map ~/NarrativeAnnotation/resources/pubtator_central_taggermap.json

# Next, tag the documents with our PharmDictTagger
python3 ~/NarrativeAnnotation/src/narrant/preprocessing/dictpreprocess.py -i $UPDATES_PUBTATOR -c PubMed --skip-load --workers 2


# Execute Cleaning Rules for Tagging
echo 'cleaning Tag table with hand-written rules'
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=mininguser password=F2M>FAJL2ptVm)W" -f $TAG_CLEANING_SQL


# Perform classification
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  -i $UPDATES_PUBTATOR -c PubMed -r ~/NarrativeAnnotation/resources/classification/pharmaceutical_classification_rules.txt --cls Pharmaceutical -w 15 --skip-load
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  -i $UPDATES_PUBTATOR -c PubMed -r ~/NarrativeAnnotation/resources/classification/plant_specific_rules.txt --cls PlantSpecific -w 15 --skip-load
python3 ~/NarrativeAnnotation/src/narrant/classification/apply_svm.py -i $UPDATES_PUBTATOR -c PubMed ~/pharmaceutical_technology_articles_svm.pkl --cls PharmaceuticalTechnology --workers 2

# Load Pharmaceutical Journals as Pharmaceutical Technology
python3 ~/NarrativeAnnotation/src/narrant/backend/export_articles_from_journals.py ~/NarrativeAnnotation/resources/classification/pharmaceutical_technology_journals.txt $PHARM_TECH_IDS -c PubMed
python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py  $PHARM_TECH_IDS PharmaceuticalTechnology -c PubMed


# Load all LitCOVID + Long Covid classifications
wget https://www.ncbi.nlm.nih.gov/research/coronavirus-api/export/all/tsv -O $LITCOVID_ID_FILE
wget 'https://www.ncbi.nlm.nih.gov/research/coronavirus-api/export/tsv?text=e_condition%3ALongCovid&filters=%7B%7D' -O $LONGCOVID_ID_FILE

python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py $LITCOVID_ID_FILE LitCovid -c PubMed
python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py $LONGCOVID_ID_FILE LongCovid -c PubMed

# Finally, all files have been tagged
python3 ~/NarrativeAnnotation/narrant/analysis/export_relevant_pharmaceutical_documents.py $UPDATED_IDS -c PubMed

# Do the statement extraction via our Pipeline
python3 ~/NarrativeAnnotation/src/narrant/extraction/pharmaceutical_pipeline.py -bs 50000 --idfile $UPDATED_IDS -c PubMed -et PathIE --workers 2 --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json


