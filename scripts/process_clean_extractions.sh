# get the highest predication id
PREDICATION_MINIMUM_UPDATE_ID_FILE=/data/FID_Pharmazie_Services/narrative_data_update/db_highest_predication_id.txt
PREDICATION_MINIMUM_UPDATE_ID=$(<"$PREDICATION_MINIMUM_UPDATE_ID_FILE")
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


echo "Highest predication id is $PREDICATION_MINIMUM_UPDATE_ID"

# Do the canonicalizing step
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/cleaning/canonicalize_predicates.py --word2vec_model /data/FID_Pharmazie_Services/narrative_data_update/BioWordVec_PubMed_MIMICIII_d200.bin --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Apply the rules
python3 ~/NarrativeAnnotation/src/narrant/cleaning/pharmaceutical_rules.py --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Execute Cleaning Rules for Predications
python3 ~/NarrativeAnnotation/src/narrant/cleaning/clean_predication_sql.py
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Export the highest known id
python3 ~/NarrativeIntelligence/lib/KGExtractionToolbox/src/kgextractiontoolbox/backend/export_highest_predication_id.py $PREDICATION_MINIMUM_UPDATE_ID_FILE
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi
