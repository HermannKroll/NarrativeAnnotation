# Classification
We support two classification modes. 
- A rule-based classification
- Supervised classification via Support Vector Machines


## Rule-based Classification
The underlying toolbox supports the classification of texts by regular expressions. 
Therefore, we apply a simple search whether a regular expression can be found within a document's text.
If the expression can be matched, we classify the document as belonging to the specified class.
```
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  \
-c COLLECTION -r EXPRESSION_FILE --cls CLASS -w 15
```

Again, the documents of a whole collection are classified if just using the collection flag.
However, if collections grow, this can become slow since the whole collection is classified every time.
If you want to specify a document file, just use the **-i** argument:
```
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py  \
-i docs.json -c COLLECTION -r EXPRESSION_FILE --cls CLASS -w 15
```

If documents are not present in the database, the script will automatically load them. 
Again, you can specify the **--skip-load** argument to skip loading.

Arguments:
- **COLLECTION**: specifies the document collection
- **EXPRESSION_FILE**: path to a .txt file with regular expressions
- **CLS**: document class if one rule is matched
- **w**: number of parallel works


## Classification File Format
Regular expressions must be stored as a .txt file. 
Each line represents a regular expression.
We support the following notation:
- \* as the known wildcard operation
- AND to force that two expressions must be matched within a text (Either both or no match)
- w/1, w/2, ... to allow an arbitrary number of words between two expressions

Note that we do not support more advanced expressions for now (due to complexity and performance).

A pharmaceutical example file is shown below:
```
Saponin*
Terpen*
Traditional Knowledge
Traditional w/1 Medicine
Triterpen*
Unani
volatile w/1 compound*
target* AND thera*
target* AND molec*
```

## Pharmaceutical Document classification
At the moment, we have two classification rule files available: Pharmaceutical and PlantSpecific:
- [pharmaceutical classification rule](resources/classification/pharmaceutical_classification_rules.txt)
- [Plant specific classification rules](resources/classification/plant_specific_rules.txt)

Run the pharmaceutical classification via:
```
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py \
    -i docs.json -c PubMed --cls Pharmaceutical -w 15 --skip-load \
    -r ~/NarrativeAnnotation/resources/classification/pharmaceutical_classification_rules.txt  
```

Run the plant specific classification via:
```
python3 ~/NarrativeAnnotation/lib/KGExtractionToolbox/src/kgextractiontoolbox/entitylinking/classification.py \
    -i docs.json -c PubMed --cls PlantSpecific -w 15 --skip-load \
    -r ~/NarrativeAnnotation/resources/classification/plant_specific_rules.txt 

```

Again you might adjust the arguments.

## Supervised Classification

How to make the model available?

Apply the classification to documents via the following command:
```
python3 ~/NarrativeAnnotation/src/narrant/classification/apply_svm.py \
    ~/models/pharmaceutical_technology_articles_svm.pkl \ 
    -i docs.json -c PubMed --cls PharmaceuticalTechnology --workers 2
```

Again specify the parameters as you need it.
Keep in mind, that it might be a good idea to only classify delta document files.
Classifying a whole collection forces a classification for every document.
We do not store whether a document has already been classified before (unlike the entity linking pipeline). 
If necessary, we could implement it in the future.

### Pharmaceutical Technology Training
We discussed how to train a model on GitHub:
- https://github.com/HermannKroll/NarrativeIntelligence/issues/151

We decided to export a list of document ids belonging to pharmaceutical technology journals.
These documents are our positive examples.
Then, we randomly sampled negative documents which do not belong to these journals.
Finally, we can train a SVM to predict whether the text belongs to the class.
We compared SVMs to other machine learning models in our issue.
However, SVMs were the best trade-off between performance and accuracy. 

The list of journals is available here:
- [list of pharmaceutical technology journals](resources/classification/pharmaceutical_technology_journals.txt)

To reproduce our training, export the document ids fist.
```
python3 ~/NarrativeAnnotation/src/narraint/backend/export_article_ids_from_journals.py \
    ~/NarrativeAnnotation/resources/classification/pharmaceutical_technology_journals.txt \
    pharmaceutical_technology_articles.ids -c PubMed
```

Then invoke the SVM training. 
However, this step may take several days (up to weeks) because we perform an extensive hyperparameter search.
Therefore, we split data into train, test and val. 
We train the SVM on train, search for good hyperparameters on val and evaluate the final performance on test.


Run:
```
python3 ~/NarrativeAnnotation/src/narrant/classification/train_svm.py \
    pharmaceutical_technology_articles.ids pharmaceutical_technology_articles_svm.pkl -c PubMed -s 50000 --workers 30
```