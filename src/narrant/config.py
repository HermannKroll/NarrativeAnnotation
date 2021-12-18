"""
This module contains constants which point to important directories.
"""
import os

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
MESH_SUPPLEMENTARY_ID_TO_HEADING_INDEX_FILE = os.path.join(TMP_DIR, 'supp2021_id2heading.pkl')

# CHEMBL
CHEMBL_DRUG_CSV = os.path.join(RESOURCE_DIR, "chembl2021.csv")

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
PREPROCESS_CONFIG = os.path.join(CONFIG_DIR, 'preprocess.json')

# Backend for Tagging
BACKEND_CONFIG = os.path.join(CONFIG_DIR, "backend.json")

# Dict Tagger
DICT_TAGGER_BLACKLIST = os.path.join(RESOURCE_DIR, "dict_tagger_blacklist.txt")

# DosageForm Tagger
DOSAGE_FORM_TAGGER_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, "dosage_form_cache.pkl")
DOSAGE_ADDITIONAL_DESCS = os.path.join(RESOURCE_DIR, "df_additional_descs.txt")
DOSAGE_ADDITIONAL_DESCS_TERMS = os.path.join(RESOURCE_DIR, "df_additional_descs_terms.txt")
DOSAGE_FID_DESCS = os.path.join(RESOURCE_DIR, "df_fid_descriptors.txt")

# Drug Tagger
DRUG_TAGGER_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, "drug_cache.pkl")
CHEMBL_CHEMICAL_DATABASE_FILE = os.path.join(RESOURCE_DIR, "chembl_chemicals.txt")
CHEMBL_BLACKLIST_FILE = os.path.join(RESOURCE_DIR, "chembl_blacklist.txt")
CHEMBL_CHEMICAL_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, "chemical_cache.pkl")

# Excipient Tagger
EXCIPIENT_TAGGER_DATABASE_FILE = os.path.join(RESOURCE_DIR, 'excipient_database_2020.csv')
EXCIPIENT_CURATED_LIST_FILE = os.path.join(RESOURCE_DIR, "excipients_curated2021.txt")
EXCIPIENT_TAGGER_DRUGBANK_EXCIPIENT_FILE = os.path.join(RESOURCE_DIR, 'chembl_excipients.txt')
EXCIPIENT_TAGGER_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, "excipient_cache.pkl")

# Disease Tagger
DISEASE_TAGGER_DATABASE_FILE = MESH_DESCRIPTORS_FILE
DISEASE_TAGGER_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, 'disease_cache.pkl')

# Method Tagger
METHOD_CLASSIFICATION_FILE = os.path.join(RESOURCE_DIR, "method_classification.tsv")
METHOD_TAGGER_DATABASE_FILE = MESH_DESCRIPTORS_FILE
METHOD_TAGGER_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, 'method_cache.pkl')

LAB_METHOD_TAGGER_DATABASE_FILE = MESH_DESCRIPTORS_FILE
LAB_METHOD_TAGGER_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, 'lab_method_cache.pkl')

# Plant Family Tagger
PLANT_FAMILTY_DATABASE_FILE = os.path.join(RESOURCE_DIR, 'plant_families_2020.txt')
PLANT_FAMILTY_INDEX_CACHE = os.path.join(TMP_DIR_TAGGER, 'plant_families_cache.pkl')
