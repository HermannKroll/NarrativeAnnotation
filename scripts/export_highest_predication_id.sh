PREDICATION_MINIMUM_UPDATE_ID_FILE=/home/"$USER"/db_highest_predication_id.txt
PREDICATION_MINIMUM_UPDATE_ID=$(<"$PREDICATION_MINIMUM_UPDATE_ID_FILE")

echo "Highest predication id is $PREDICATION_MINIMUM_UPDATE_ID"


# Export highest ID for cleaning
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/backend/export_highest_predication_id.py $PREDICATION_MINIMUM_UPDATE_ID_FILE
if [[ $? != 0 ]]; then
    echo "Previous script returned exit code != 0 -> Stopping pipeline."
    exit -1
fi