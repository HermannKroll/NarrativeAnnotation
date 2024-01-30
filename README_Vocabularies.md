# Vocabulary Overview

## Internal Vocabulary
| Name               | Description                                                                     | Ontology | Dependencies                                                                                                                                                                                                                                                                   | 
|--------------------|---------------------------------------------------------------------------------| ------ |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| Chemical           | general chemicals                                                               | ChEMBL | [ChEMBL DB](resources/vocabularies/drug/chembl29.csv) + [Chembl Chemical Classification](resources/vocabularies/chemical/chembl_chemicals.txt)                                                                                                                                 |
| Drug               | active ingredients/drug/substances (no trade names)                             |  ChEMBL | [ChEMBL DB](resources/vocabularies/drug/vocabulary.tsv) + [Blacklist](resources/vocabularies/drug/chembl_blacklist.txt)                                                                                                                                                        |
| Disease            | diseases, symptoms, side effects                                                | MeSH | [MeSH Tree](resources/vocabularies/disease/mesh_tree_numbers.txt) + [Vocabulary](resources/vocabularies/disease/vocabulary.tsv)                                                                                                                                                |
| Dosage Form        | forms in which a drug is administered / bound                                   | MeSH + FID Vocab. | [MeSH Tree](resources/vocabularies/dosageform/mesh_tree_numbers.txt) + [MeSH Descriptors](resources/vocabularies/dosageform/mesh_descriptors.txt) + [Vocabulary](resources/vocabularies/dosageform/vocabulary.tsv)                                                             | 
| Excipient          | ingredients / chemicals that are used in dosage forms                           | ChEMBL + Plain | [Crawled-Excipient Database](resources/vocabularies/excipient/excipient_database_2020.csv) + [Chembl Excipient Classification](resources/vocabularies/excipient/chembl_excipients.txt) + [Additional Excipients](resources/vocabularies/excipient/excpients_curated2021.txt)   |
| HealthStatus       | Status for patients (women, men, alcoholics, ...)                               | MeSH | [MeSH Tree](resources/vocabularies/healthstatus/mesh_tree_numbers.txt)                                                                                                                                                                                                         |
| Method             | general methods for investigation                                               | MeSH | [MeSH Tree](resources/vocabularies/method/mesh_tree_numbers.txt)                                                                                                                                                                                                               |
| LabMethod          | manually selected subset of Methods that are classfied as labor relevant methods | MeSH  | [Own Classification](resources/vocabularies/labmethod/method_classification.tsv)                                                                                                                                                                                               |
| PlantFamiliy/Genus | Plants (Families, Genus). Additional Cleaning is performed.                     | Plain | [Plant Familiy File](resources/vocabularies/plant_family_genus/plant_families_2020.txt) + [Plant Familiy Wikidata](resources/vocabularies/plant_family_genus/plant_family_wikidata.txt) + [Cleaning Rules](resources/vocabularies/plant_family_genus/plant_specific_rules.txt) 
| Target             | Pharmaceutical Targets (proteases, lactamase, ...)                              |  ChEMBL | [ChEMBL DB](resources/vocabularies/target/vocabulary.tsv)                                                                                                                                                      |
| Vaccine            | Vaccines for different diseases                                                 | MeSH + Wikidata | [MeSH Tree](resources/vocabularies/vaccine/mesh_tree_numbers.txt) + [Vocabulary](resources/vocabularies/vaccine/vocabulary.tsv)                                                                                                                                                | 

Plain means that we do not link the entity against identifiers. 
We just map the text mention to the corresponding entity type similar to entity recognition.
For example, "cannabis" will be mapped to the Plant "Cannabis".


## External Data Sources
We utilize the following external sources to build our vocabularies.

| Name | Source  | 
| ------ | ------ | 
| ChEMBL |  https://www.ebi.ac.uk/chembl/ | 
| Excipient Database | https://www.accessdata.fda.gov/scripts/cder/iig/index.cfm |
| MeSH | https://meshb.nlm.nih.gov  | 
| Wikidata | https://www.wikidata.org/ | 


## External Tool Usage
| Name | Description | External Data Sources | 
| ------ | ------ | ------ | 
| Chemical | ... | ... |
| Disease | ... | ... |
| Gene | ... | ... |
| Species | ... | ... |



# Update the MeSH Vocabularies

# Plant Family/Genus (Wikidata)
Execute the following [query](https://query.wikidata.org/#%23Families%0ASELECT%20%3Ftaxonname%20WHERE%20%7B%0A%20%20%3Fitem%20wdt%3AP31%20wd%3AQ16521%20%3B%0A%20%20%20%20%20%20%20%20wdt%3AP105%20wd%3AQ35409%20%3B%0A%20%20%20%20%20%20%20%20wdt%3AP225%20%3Ftaxonname%20%3B%0A%20%20%20%20%20%20%20%20wdt%3AP1421%20%3FGRIN%20.%0A%20%20%0A%7D):
```
#Families
SELECT ?taxonname WHERE {
  ?item wdt:P31 wd:Q16521 ;
        wdt:P105 wd:Q35409 ;
        wdt:P225 ?taxonname ;
        wdt:P1421 ?GRIN .
  
}
ORDER BY ASC(?taxonname)
```
Export results as a TSV file and store the results to:
```
resources/vocabularies/plant_family_genus/plant_family_wikidata.txt
```

# Drugs + Organisms (ChEMBL)
We implemented crawlers to crawle the Drugs and Organisms from the ChEMBL API.

Update the drug vocabulary via:
```
python src/narrant/vocabularies/drug_vocabulary.py
```
Update the organism vocabulary via:
```
python src/narrant/vocabularies/organism_vocabulary.py
```
Both scripts will update the vocabulary.tsv in the corresponding resources folders (drug + target). 


# Disease Long Covid 19 Wikidata:
To derive more disease synonyms for long Covid 19:
```
SELECT ?item ?itemLabel ?altLabel WHERE {
   VALUES ?item {wd:Q100732653} 
   OPTIONAL { ?item skos:altLabel ?altLabel . FILTER (lang(?altLabel) = "en") }      
   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }     
}
```
Save it in the [vocabulary for diseases](resources/vocabularies/disease/vocabulary.tsv). 


# Vaccine
Query Wikidata vaccines
```
#Vaccines 
SELECT ?itemID ?ent_type ?itemLabel  (GROUP_CONCAT(?altLabel;separator=";") AS ?synonyms)
WHERE 
{
  VALUES ?vacc {wd:Q87719492 wd:Q85795487 wd:Q134808 wd:Q105967696 wd:Q58624061 wd:Q1810913 wd:Q58630730 wd:Q3560939 wd:Q28051899 wd:Q96841548 wd:Q578537 wd:Q85795487 wd:Q97153933 wd:Q58623657 wd:Q99518999} 
  ?item wdt:P31+|wdt:P279+ ?vacc;
  OPTIONAL { ?item wdt:P486 ?mesh }
  BIND ("Vaccine" AS ?ent_type) .
  BIND (CONCAT('MESH:', ?mesh) AS ?meshLabel).
  BIND (if (exists { ?item wdt:P486 ?mesh}, ?meshLabel, ?item) AS ?itemID)

  
  ?item skos:altLabel ?altLabel . FILTER (lang(?altLabel) = "en")       
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }     
}
GROUP BY ?itemID ?itemLabel ?ent_type
ORDER BY ASC(?itemLabel)
```

Download the file as a .tsv file from the Wikidata query endpoint.
The .tsv must be converted to our internal vocabulary format. 
Use MeSH Descriptors instead of Wikidata ids if possible.