
# Concept/Entity Indexes
If you want to export in our specified XML format, you need to create some indexes before you can use the XML export.
There are two index modes:
- a complete index (takes more space, but only computed once)
- a partial index (only includes tagged entity ids in our db, smaller but must be recreated if new entites are tagged)


Partial index: Run the following script to create a **partial index**.
The script will ask you if your database connection is configured properly. 
```
python3 src/narrant/build_all_indexes.py
```
...and enter yes if the correct database connection is selected.
This might take a while and will build all required indexes. 
Attention: indexes for genes and species will only be build for those tag ids that have been annotated so far. 
If you annotate more documents, you **must** rebuild the indexes. 


Complete index: You can prevent rebuilding the index creation by creating a complete entity index. 
Therefore, run:
```
python3 src/narrant/build_all_indexes.py --complete
```

# Export Annotation Data
Please ensure, that all indexes have been build (see previous step).


### JSON UB Format
Finally, you can export the documents in a JSON Format:
```
python3 src/narrant/backend/exports/json_ub_export.py OUTPUT_FILE -c COLLECTION_NAME
```

The written JSON content looks like: (Note URI do not exists for all entities)

```
{                                                                                                                                                                                                                                                |
     "id": 92116,                                                                                                                                                                                                                                    
     "tags": [
          {
               "id": "31285",
               "mention": "Trypanosoma gambiense",
               "start": 66,
               "end": 87,
               "type": "Species",
               "name": "Trypanosoma brucei gambiense",
               "source": "NCBI Taxonomy",
               "URI": "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=31285"
          },
          {
               "id": "MESH:D014355",
               "mention": "Trypanosoma",
               "start": 258,
               "end": 269,
               "type": "Disease",
               "name": "Chagas Disease",
               "source": "MeSH",
               "URI": "https://meshb.nlm.nih.gov/record/ui?ui=D014355"
          },
          {
               "id": "31285",
               "mention": "gambiense",
               "start": 270,
               "end": 279,
               "type": "Species",
               "name": "Trypanosoma brucei gambiense",
               "source": "NCBI Taxonomy",
               "URI": "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=31285"
          },
          {
               "id": "CHEMBL284328",
               "mention": "ethidium bromide",
               "start": 369,
               "end": 385,
               "type": "Drug",
               "name": "Homidium bromide",
               "source": "ChEMBL",
               "URI": "https://www.ebi.ac.uk/chembl/compound_report_card/CHEMBL284328"
          }
    ]
}
```


You may export the document content via:
```
python3 src/narrant/backend/exports/json_ub_export.py OUTPUT_FILE -c COLLECTION_NAME -d
```

- the optional **-d** will force to export the document content (title and abstract)

The written JSON content looks like: (Note **URI** do not exists for all entities)
```
{                                                                                                                                                                                                                                                |
     "id": 92116,    
     "title": "In situ microspectrofluorometry of nuclear and kinetoplast DNA in Trypanosoma gambiense.",                                                                                                                                            
     "abstract": "Using a spectrofluorometer with the Zeiss Universal Micro-Spectrophotometer 1 (UMSP 1), [...]",                                                                                                                                                                                                                                                 
     "tags": [
          {
               "id": "31285",
               "mention": "Trypanosoma gambiense",
               "start": 66,
               "end": 87,
               "type": "Species",
               "name": "Trypanosoma brucei gambiense",
               "source": "NCBI Taxonomy",
               "URI": "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=31285"
          } 
      ]
}
```

### Export XML UB (Deprecated)
Finally, you can export the documents:
```
python3 src/narrant/backend/exports/xml_export.py output_dir -c COLLECTION_NAME
```
See help for parameter description. The output format looks like: document_id.xml and the content:



```
<?xml version="1.0" ?>
<document>
   <tag source="NCBI Gene">eukaryotic translation initiation factor 2 alpha kinase 2</tag>
   <tag source="NCBI Gene">Atf4</tag>
   <tag source="NCBI Gene">DNA damage inducible transcript 3</tag>
   <tag source="NCBI Gene">DDIT3</tag>
   <tag source="NCBI Gene">eukaryotic translation initiation factor 2 alpha kinase 3</tag>
   <tag source="NCBI Gene">EIF2AK3</tag>
   <tag source="DrugBank">Toyocamycin</tag>
   <tag source="NCBI Taxonomy">house mouse</tag>
   <tag source="NCBI Taxonomy">Mus musculus</tag>
   <tag source="MeSH">Wounds and Injuries</tag>
   <tag source="MeSH">Death</tag>
</document>
```

# Translating document formats 
In this section, we describe how to convert different formats into JSON format.
## Patents
Suppose you have the Patents available text file (see the following example).
```
oai:tib.eu:epa:EP3423078|T-CELL MODULATORY MULTIMERIC POLYPEPTIDES AND METHODS OF USE THEREOF
oai:tib.eu:epa:EP3423078|The present disclosure provides variant immunomodulatory polypeptides, and fusion polypeptides comprising the variant immunomodulatory peptides. The present disclosure provides T-cell modulatory multimeric polypeptides, and compositions comprising same, where the T-cell modulatory multimeric polypeptides comprise a variant immunomodulatory polypeptide of the present disclosure. The present disclosure provides nucleic acids comprising nucleotide sequences encoding the T-cell modulatory multimeric polypeptides, and host cells comprising the nucleic acids. The present disclosure provides methods of modulating the activity of a T cell; the methods comprise contacting the T cell with a T-cell modulatory multimeric polypeptide of the present disclosure.
oai:tib.eu:epa:EP3424500|PHARMACEUTICAL COMPOSITION COMPRISING PYRROLO-FUSED SIX-MEMBERED HETEROCYCLIC COMPOUND
oai:tib.eu:epa:EP3424500|The present invention provides a pharmaceutical composition comprising a pyrrolo-fused six-membered heterocyclic compound or a pharmaceutically acceptable salt of the compound. Specifically, the invention provides a pharmaceutical composition comprising 5-(2-diethylamino-ethyl)-2-(5-fluoro-2-oxo-1,2-dihydro-indol-3-ylidene-methyl)-3-met hyl-1,5,6,7-tetrahydro-pyrrolo[3,2-c]pyridin-4-one or a pharmaceutically acceptable salt thereof, and at least one water soluble filler. The pharmaceutical composition of the invention features rapid dissolution and good stability.
```
You can convert the patents by calling:
```
python3 src/narrant/pubtator/translation/patent.py PATENT_FILE OUTPUT -c COLLECTION
```

The Patent converter will automatically convert source ids (oai:tib.eu:epa:EP3423078) to internal ids.

The following output will be produced:
```
[
    {
        "id": 1,
        "title": "T-Cell Modulatory Multimeric Polypeptides And Methods Of Use Thereof",
        "abstract": "The present disclosure provides variant immunomodulatory polypeptides [...]"
    },
    {
        "id": 2,
        "title": "Pharmaceutical Composition Comprising Pyrrolo-Fused Six-Membered Heterocyclic Compound",
        "abstract": "The present invention provides a pharmaceutical composition [...]"
    }
]
```

### Exporting Patents
Finally, you can export the patents via:
```
python3 src/narrant/backend/exports/json_ub_export.py OUTPUT -c COLLECTION_NAME --translate_ids
```
The argument **--translate_ids** will force the script to translate the patent ids back to their original ids.
