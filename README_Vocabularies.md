
# Plant Family/Genus

Plant Family Wikidata:


Execute the following [query](https://query.wikidata.org/#%23Families%0ASELECT%20%3Ftaxonname%20WHERE%20%7B%0A%20%20%3Fitem%20wdt%3AP31%20wd%3AQ16521%20%3B%0A%20%20%20%20%20%20%20%20wdt%3AP105%20wd%3AQ35409%20%3B%0A%20%20%20%20%20%20%20%20wdt%3AP225%20%3Ftaxonname%20%3B%0A%20%20%20%20%20%20%20%20wdt%3AP1421%20%3FGRIN%20.%0A%20%20%0A%7D):
```
#Families
SELECT ?taxonname WHERE {
  ?item wdt:P31 wd:Q16521 ;
        wdt:P105 wd:Q35409 ;
        wdt:P225 ?taxonname ;
        wdt:P1421 ?GRIN .
  
}
```
Export results as a TSV file and store the results to:
```
resources/vocabularies/plant_family_genus/plant_family_wikidata.txt
```

# Drugs

ChEBML Update:

We need a database environment for it. 
Either SQLlite or Postgres. 
We stick to Postgres in the following.

Download the latest version from [ChEMBL](https://chembl.gitbook.io/chembl-interface-documentation/downloads).
```
pg_restore --no-owner -h 127.0.0.1 -p 5432 -U tagginguser -d chembldb chembl_29_postgresql.dmp
```

After database has been loaded, query chembl drugs:
```
SELECT md.chembl_id, md.pref_name, ms.synonyms
FROM molecule_dictionary md LEFT JOIN molecule_synonyms ms ON (md.molregno = ms.molregno and ms.syn_type <> 'TRADE_NAME')
WHERE pref_name IS NOT NULL
GROUP BY md.chembl_id, md.pref_name, ms.synonyms
ORDER BY md.chembl_id;
```

Save results as a csv and store it in ...

# Long Covid 19 Wikidata:
To derive more disease synonyms for long Covid 19:
```
SELECT ?item ?itemLabel ?altLabel WHERE {
   VALUES ?item {wd:Q100732653} 
   OPTIONAL { ?item skos:altLabel ?altLabel . FILTER (lang(?altLabel) = "en") }      
   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }     
}
```

Save it in the vocabulary for diseases.


# Vaccine
Query Wikidata vaccines
```
#Vaccines 
SELECT ?item  ?itemLabel  ?mesh (GROUP_CONCAT(?altLabel;separator=";") AS ?labels)
WHERE 
{
  VALUES ?vacc {wd:Q87719492 wd:Q85795487 wd:Q134808 wd:Q105967696 wd:Q58624061 wd:Q1810913 wd:Q58630730 wd:Q3560939 wd:Q28051899 wd:Q96841548 wd:Q578537 wd:Q85795487 wd:Q97153933 wd:Q58623657 wd:Q99518999} 
  ?item wdt:P31+|wdt:P279+ ?vacc;
  OPTIONAL { ?item wdt:P486 ?mesh }
  
  ?item skos:altLabel ?altLabel . FILTER (lang(?altLabel) = "en")       
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }     
}
GROUP BY ?item ?itemLabel ?mesh
ORDER BY ASC(?itemLabel)
```

file must be converted to our internal vocabulary format. 
Use MeSH Descriptors instead of Wikidata ids if possible.