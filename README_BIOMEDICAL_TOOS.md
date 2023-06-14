
### Create a directory for the tagger tools
```
mkdir ~/tools
```
### Third-Party Taggers
Download [GNormPlus](https://www.ncbi.nlm.nih.gov/research/bionlp/Tools/gnormplus/) and [TaggerOne](https://www.ncbi.nlm.nih.gov/research/bionlp/tools/taggerone/). Unzip both and move the directories into tools. 
```
tools/
  GNormPlusJava/
  TaggerOne-0.2.1/
```
Both tools require a Java installation. To use TaggerOne, see its readme file. Some models must be build manually.

### Tagger Configuration
Configure the tagger locations for the project
```
cd NarrativeAnnotation/config/
cp entity_linking.prod.json entity_linking.json
nano preprocess.json
```
Enter your GNormPlus and TaggerOne root paths
```
{
  "taggerOne": {
    "root": "../TaggerOne-0.2.1",
    "model": "models/model_BC5CDRJ_011.bin",
    "batchSize": 10000,
    "timeout": 10,
    "max_retries": 1
  },
  "gnormPlus": {
    "root": "../GNormPlusJava",
    "javaArgs": "-Xmx16G -Xms10G",
    "timeout": 10
  },
  "dict": {
    "max_words": 5,
    "check_abbreviation": "true",
    "custom_abbreviations": "true",
    "min_full_tag_len": 5
  },
  "stanza": {
    "document_batch_size": 1000,
    "entity_type_blocked_list": ["ORDINAL", "QUANTITY", "PERCENT"]
  }
}
```
You can ignore the other parameters for now.