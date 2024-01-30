# Entity Linking

In this section, we briefly describe how to use our pipeline.
For the examples below, we suppose you to be in the correct directory. So,
```
cd ~/NarrativeAnnotation/
```

The idea of our pipeline is based on entity types. For example, if a user want to annotate drugs in text, then the corresponding annotation tool will be invoked. 
Hence, the users could specify which entity types they want to annotate in texts.
## Annotation Data (Tags)
The tagging pipeline produces tags. A tag represents an annotation and consists of a:
- document id (int)
- document collection (string)
- start position in text (int)
- end position in text (int)
- entity str (the annotated text sequence, string)  
- entity id (string)
- entity type (string)



# Dictionary-based Entity Linking
There are two options to run our entity linking pipeline:
- You can load documents into the collection by hand. The pipeline can then annotate new documents in the whole collection. 
- You can also specify a document file. Then, documents are loaded automatically and tagged after wise. 

For the first option, leave out the **-i test.json** argument and just specify a collection.


You can invoke our own dictionary-based tagger pipeline via:
```
python3 src/narrant/entitylinking/dictpreprocess.py -i test.json --collection test
```
This call will invoke the pipeline to annotate all known entity types.
The pipeline annotates Diseases, Dosage Forms, Drugs, Chemicals, Excipients, Methods, LebMethods and Plant Families.
The first run will build all necessary indexes that will speed up further runs. 
So, the first run may take a bit.


You can may also speedup the tagging process. 
You invoke multiple parallel workers. 
The number of parallel workers can be specified as follows:
```
python3 src/narrant/entitylinking/dictpreprocess.py -i test.json --collection test --workers 10
```

If you are certain that all documents are already in the database, you may skip the loading phase by:
```
python3 src/narrant/entitylinking/dictpreprocess.py -i test.json --collection test --skip-load
```

The pipeline will work in a temporary directory (random directory in /tmp/) and remove it if the task is completed. If you want to work in a specified directory, use
```
python3 src/narrant/entitylinking/dictpreprocess.py -i test.json --collection test --workdir temp/
```
If you specify a directory, the temporary created files and logs won't be removed automatically.


## TaggerOne and GNormPlus (ThirdParty)
In addition to our own annotation tools, we build support for two frequently used biomedical tools. 
TaggerOne supports the annotation of Chemicals and Diseases (deprecated).
GNormPlus supports the annotation of Genes and Species.


Annotate documents via GNormPlus:

```
python3 lib/KGExtractionToolbo/src/kgextractiontoolbox/entitylinking/biomedical_entity_linking.py test.json --collection test --tagger-one 
```

Annotate documents via TaggerOne (deprecated):
```
python3 lib/KGExtractionToolbo/src/kgextractiontoolbox/entitylinking/biomedical_entity_linking.py test.json --collection test --gnormplus
```

The pipeline will invoke the taggers to tag the documents. The document corpus is *test*.
The tools can be invoked by:
- tagger-one means that TaggerOne will be used to annotate Chemicals and Diseases.
- gnormplus means that GNormPlus will be used to annotate Genes and Species.

Note: only one tagger can be selected in a tagging process.

The pipeline will work in a temporary directory and remove it if the task is completed. 
If you want to work in a specified directory, use
```
python3 lib/KGExtractionToolbo/src/kgextractiontoolbox/entitylinking/biomedical_entity_linking.py --collection test --workdir temp/ --gnormplus 
```
If you specify a directory, the temporary created files and logs won't be removed automatically.