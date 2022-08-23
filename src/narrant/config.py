"""
This module contains constants which point to important directories.
"""
import os
from pathlib import Path


def search_config(start: Path, dirname: Path, filename: Path):
    if not start.is_dir():
        return None
    if not (start/dirname).is_dir() or not (start/dirname/filename).is_file():
        return search_config(start/"..", dirname, filename)
    else:
        return (start/dirname/filename).resolve()


GIT_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

DATA_DIR = os.path.join(GIT_ROOT_DIR, "data")
RESOURCE_DIR = os.path.join(GIT_ROOT_DIR, "resources")
CONFIG_DIR = os.path.join(GIT_ROOT_DIR, "config")
TMP_DIR = os.path.join(GIT_ROOT_DIR, "tmp")
TMP_DIR_TAGGER = os.path.join(TMP_DIR, 'tagger')

if not os.path.isdir(TMP_DIR):
    os.makedirs(TMP_DIR)

if not os.path.isdir(TMP_DIR_TAGGER):
    os.makedirs(TMP_DIR_TAGGER)

# MeSH Ontology Index File
MESH_ONTOLOGY_INDEX_FILE = os.path.join(TMP_DIR, "mesh_ontology_index.pkl")

# MESH
MESH_DESCRIPTORS_FILE = os.path.join(DATA_DIR, "desc2022.xml")
MESH_SUPPLEMENTARY_FILE = os.path.join(DATA_DIR, "supp2022.xml")
MESH_ID_TO_HEADING_INDEX_FILE = os.path.join(TMP_DIR, 'desc2022_id2heading.pkl')
MESH_SUPPLEMENTARY_ID_TO_HEADING_INDEX_FILE = os.path.join(TMP_DIR, 'supp2022_id2heading.pkl')

# CHEMBL
CHEMBL_DRUG_CSV = os.path.join(RESOURCE_DIR, "vocabularies/drug/chembl29.csv")

# DrugBank
DRUGBANK_XML_DUMP = os.path.join(DATA_DIR, "drugbank2021.xml")

# GENE
GENE_FILE = os.path.join(DATA_DIR, 'gene_info_2022.gz')
GENE_INDEX_FILE = os.path.join(TMP_DIR, 'gene_info_2022_id2name.pkl')
GENE_TO_HUMAN_ID_FILE = os.path.join(TMP_DIR, 'gene_2022_to_human_id.pkl')

# Taxonomy Names 2020
TAXONOMY_FILE = os.path.join(RESOURCE_DIR, 'taxonomy_names_2020.gz')
TAXONOMY_INDEX_FILE = os.path.join(TMP_DIR, 'taxonomy_name_index.pkl')

# Preprocessing
PREPROCESS_CONFIG = str(search_config(Path(CONFIG_DIR) / '..', Path('config'), Path('preprocess.json')))

# Backend for Tagging
#BACKEND_CONFIG = os.path.join(CONFIG_DIR, "backend.json")
BACKEND_CONFIG = str(search_config(Path(CONFIG_DIR)/'..', Path('config'), Path('backend.json')))

# Dict Tagger
DICT_TAGGER_BLACKLIST = os.path.join(RESOURCE_DIR, "dict_tagger_blacklist.txt")

# DosageForm Tagger
DOSAGEFORM_TAGGER_VOCAB_DIRECTORY = os.path.join(RESOURCE_DIR, 'vocabularies/dosageform')
DOSAGEFORM_TAGGER_VOCAB = os.path.join(DOSAGEFORM_TAGGER_VOCAB_DIRECTORY, "vocabulary.tsv")


# Drug Tagger
CHEMBL_CHEMICAL_DATABASE_FILE = os.path.join(RESOURCE_DIR, "vocabularies/chemical/chembl_chemicals.txt")
CHEMBL_BLACKLIST_FILE = os.path.join(RESOURCE_DIR, "vocabularies/drug/chembl_blacklist.txt")

# Excipient Tagger
EXCIPIENT_TAGGER_DATABASE_FILE = os.path.join(RESOURCE_DIR, 'vocabularies/excipient/excipient_database_2020.csv')
EXCIPIENT_CURATED_LIST_FILE = os.path.join(RESOURCE_DIR, "vocabularies/excipient/excipients_curated2021.txt")
EXCIPIENT_TAGGER_DRUGBANK_EXCIPIENT_FILE = os.path.join(RESOURCE_DIR, 'vocabularies/excipient/chembl_excipients.txt')

# Disease Tagger
DISEASE_TAGGER_VOCAB_DIRECTORY = os.path.join(RESOURCE_DIR, 'vocabularies/disease')

# Method Tagger
METHOD_CLASSIFICATION_FILE = os.path.join(RESOURCE_DIR, "vocabularies/labmethod/method_classification.tsv")
METHOD_TAGGER_VOCAB_DIRECTORY = os.path.join(RESOURCE_DIR, "vocabularies/method")

# Plant Family Tagger
PLANT_SPECIFIC_RULES = os.path.join(RESOURCE_DIR, 'vocabularies/plant_family_genus/plant_specific_rules.txt')
PLANT_GENUS_DATABASE_FILE = os.path.join(RESOURCE_DIR, 'vocabularies/plant_family_genus/plant_families_2020.txt')
PLANT_FAMILY_WIKIDATA_FILE = os.path.join(RESOURCE_DIR, 'vocabularies/plant_family_genus/plant_family_wikidata.txt')

# Vaccine Tagger
VACCINE_TAGGER_VOCAB_DIRECTORY = os.path.join(RESOURCE_DIR, 'vocabularies/vaccine')
VACCINE_TAGGER_VOCAB = os.path.join(VACCINE_TAGGER_VOCAB_DIRECTORY, "vocabulary.tsv")
