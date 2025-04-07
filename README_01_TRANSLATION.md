# Translating Document Formats 
In this section, we describe how to convert different formats into JSON format.

An example of how to transform an external document source into our document format is given here:
```
python3 ~/NarrativeAnnotation/src/narrant/pubpharm/crawl_k10_dump.py $DOC_UPDATES --workdir $DATA_PATH --collection-filter $COLLECTION_FILTER --collection $COLLECTION --date $DATE --base-url $BASE_URL
```

### Artificial Document ids (If real IDs are not integers)
We use integers as document ids for fast joining of large tables. 
However, document ids in practice might not be integers. 
We support to generate artificial integer ids if needed.
When loading document data, just the **artificial_document_ids** flag.

```
python src/kgextractiontoolbox/documents/load_document.py DOCUMENTS.json --collection COLLECTION --artificial_document_ids
```
