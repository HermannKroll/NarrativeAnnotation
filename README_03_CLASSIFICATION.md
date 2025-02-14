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


# Load External Classification
This Readme describes the workflow to download results from PubMed and use them as a document classification in our database.
In the following, we will load the LitCovid and LongCovid collection as a showcase.

Therefore, first go to the [LitCovid Page](https://www.ncbi.nlm.nih.gov/research/coronavirus/#data-download).
Download the bibliography data as a TSV file.

Then, load the document classification via:
```
python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py all_litcovid.tsv LitCovid -c PubMed
```

You can apply a similar workflow for LongCovid documents. 
Add the condition LongCovid to your search and download the data. 
The page can be accessed [here](https://www.ncbi.nlm.nih.gov/research/coronavirus/docsum?text=e_condition:LongCovid).
Download the TSV file.
Then insert the information to our database via:
```
python3 ~/NarrativeAnnotation/src/narrant/backend/load_classification_for_documents.py longcovid.tsv LongCovid -c PubMed
```


# Create Datasets Based on Journal Lists


This section explains how to use the provided script to create datasets from document IDs based on a list of journals. The script identifies relevant and non-relevant documents and generates datasets for training, validation, and testing.

## Overview

The script processes a list of journal names (in `.xlsx` or `.txt` format) and matches them with document metadata from the database to retrieve relevant and non-relevant document IDs. It can generate either a single dataset file or split the data into train, dev, and test datasets.

## Input Files

You can use the following input files for this script:
- `pharmaceutical_technology_journals.txt`
- `2023_Pharm_Chemie_Journals.xlsx`

## Usage Instructions

Run the script with the following command:

```
python ~/NarrativeAnnotation/src/narrant/backend/create_journal_based_dataset.py --input_file INPUT_FILE --output_dir OUTPUT_DIR [--split] [--sample_size SAMPLE_SIZE] [--random_seed RANDOM_SEED]
```

### Parameters

- `--input_file`: **Required.** Path to the journal list file in `.xlsx` or `.txt` format.
- `--output_dir`: **Required.** Directory where the resulting dataset(s) will be saved.
- `--split`: Optional. If specified, the dataset will be split into train(75 %), dev(15 %), and test(15 %) sets.
- `--sample_size`: Optional. Specifies the maximum number of samples for both relevant and non-relevant documents. Default is 10000.
- `--random_seed`: Optional. Seed for random number generation to ensure reproducibility. Default is 42.

## Examples

### Example 1: Splitting the Dataset
To process `pharmaceutical_technology_journals.txt` and split the dataset into train, dev, and test sets:

```
python ~/NarrativeAnnotation/src/narrant/backend/create_journal_based_dataset.py --input_file ~/NarrativeAnnotation/resources/classification/pharmaceutical_technology_journals.txt --output_dir ./pharm_tech_output --split --sample_size 5000 --random_seed 123
```

The output directory `./pharm_tech_output` will contain the following files:
- `train_data.csv`
- `dev_data.csv`
- `test_data.csv`

### Example 2: Generating a Single Dataset
To process `2023_Pharm_Chemie_Journals.xlsx` and generate a single dataset file:

```
python ~/NarrativeAnnotation/src/narrant/backend/create_journal_based_dataset.py --input_file ~/NarrativeAnnotation/resources/classification/2023_Pharm_Chemie_Journals.xlsx --output_dir ./pharm_chem_output --sample_size 10000
```

The output directory `./pharm_chem_output` will contain the following file:
- `dataset.csv`
