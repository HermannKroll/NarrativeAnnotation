# get the highest predication id
PREDICATION_MINIMUM_UPDATE_ID_FILE=/data/FID_Pharmazie_Services/narrative_data_update/db_highest_predication_id.txt
PREDICATION_MINIMUM_UPDATE_ID=$(<"$PREDICATION_MINIMUM_UPDATE_ID_FILE")
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi


if [ "$(id -u)" == 0 ]; then
  PREDICATION_CLEANING_SQL=/root/NarrativeAnnotation/sql/clean_predication.sql
  echo "root"
fi
if [ "$(id -u)" -ne 0 ]; then
  PREDICATION_CLEANING_SQL=/home/"$USER"/NarrativeAnnotation/sql/clean_predication.sql
  echo "not root"
fi

# load the db password
source ~/NarrativeAnnotation/scripts/.secret
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
echo 'cleaning predication table with hand-written rules'
psql "host=127.0.0.1 port=5432 dbname=fidpharmazie user=mininguser password=$PSQLPW" -f $PREDICATION_CLEANING_SQL
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi

