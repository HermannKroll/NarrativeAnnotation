This Readme describes the workflow to download results from PubMed and use them as a document classification in our database.
In the following, we will load the LitCovid and LongCovid collection as a showcase.

Therefore, first go to the [LitCovid Page](https://www.ncbi.nlm.nih.gov/research/coronavirus/#data-download).
Download the bibliography data as a TSV file.
Open the TSV file and remove all comments before the CSV header.

Then, load the document classification via:
```
python3 src/narrant/backend/load_classification_for_documents.py all_litcovid.tsv LitCovid -c PubMed
```

You can apply a similar workflow for LongCovid documents. 
Add the condition LongCovid to your search and download the data. 
The page can be accessed [here](https://www.ncbi.nlm.nih.gov/research/coronavirus/docsum?text=e_condition:LongCovid).
Download the TSV file, remove the comments before the CSV header starts.
Then insert the information to our database via:
```
python3 src/narrant/backend/load_classification_for_documents.py longcovid.tsv LongCovid -c PubMed
```