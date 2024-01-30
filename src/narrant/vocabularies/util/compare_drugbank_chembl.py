import csv

from narrant.entity.entityresolver import EntityResolver
from narrant.entitylinking.enttypes import DRUG
from narrant.tools import reverse_set_index
from narrant.vocabularies.drug_vocabulary import DrugVocabulary


def main():
    vocab_without_chembl = reverse_set_index(DrugVocabulary.create_drugbank_vocabulary_from_source(expand_term=False))
    db_w_chembl, chembl = DrugVocabulary.create_drugbank_vocabulary_from_source(expand_term=False,
                                                                                use_chembl_synonyms=True,
                                                                                return_chembl_vocab=True,
                                                                                chembl_file="/home/jan/chembl_synonyms.csv")
    vocab_with_chembl, vocab_chembl = reverse_set_index(db_w_chembl), reverse_set_index(chembl)
    chembl_minus_db = {k: v - vocab_without_chembl[k] for k, v in vocab_with_chembl.items()}
    db_minus_chembl = {k: v - vocab_chembl[k] if k in vocab_chembl else set() for k, v in vocab_without_chembl.items()}
    entres = EntityResolver.instance()

    with open("/home/jan/vocab_compare.csv", "w+") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"')
        writer.writerow(["DB-ID", "Chembl minus Drugbank", "Drugbank minus Chembl"])
        for k, v in chembl_minus_db.items():
            name = entres.get_name_for_var_ent_id(k, DRUG)
            writer.writerow([k, name, " | ".join(v), "|".join(db_minus_chembl[k])])


if __name__ == '__main__':
    main()
