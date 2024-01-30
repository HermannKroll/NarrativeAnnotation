PREDICATION_CLEANING_SQL=/home/"$USER"/NarrativeAnnotation/sql/clean_predication.sql
PREDICATION_MINIMUM_UPDATE_ID_FILE="~/NarrativeAnnotation/scripts/highest_predication_id.txt"
PREDICATION_MINIMUM_UPDATE_ID=$(<"$PREDICATION_MINIMUM_UPDATE_ID_FILE")

echo "Highest predication id is $PREDICATION_MINIMUM_UPDATE_ID"

# Do the canonicalizing step
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/cleaning/canonicalize_predicates.py --word2vec_model /data/workingdir/BioWordVec_PubMed_MIMICIII_d200.bin --relation_vocab ~/NarrativeAnnotation/resources/pharm_relation_vocab.json --predicate_id_minimum $PREDICATION_MINIMUM_UPDATE_ID
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
echo 'cleaning predication table with hand-written rules'
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=mininguser password=F2M>FAJL2ptVm)W" -f $PREDICATION_CLEANING_SQL
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

# Export highest ID for cleaning
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/backend/export_highest_predication_id.py $PREDICATION_MINIMUM_UPDATE_ID_FILE
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi