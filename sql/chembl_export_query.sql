SELECT md.chembl_id, md.pref_name, ms.synonyms
FROM molecule_dictionary md LEFT JOIN molecule_synonyms ms ON (md.molregno = ms.molregno and ms.syn_type <> 'TRADE_NAME')
WHERE pref_name IS NOT NULL
GROUP BY md.chembl_id, md.pref_name, ms.synonyms
ORDER BY md.chembl_id;