SELECT md.chembl_id, md.molecule_type, md.pref_name, ms.synonyms
FROM molecule_dictionary md LEFT JOIN molecule_synonyms ms ON (md.molregno = ms.molregno)
WHERE pref_name IS NOT NULL
ORDER BY md.chembl_id;