def get_entity_source(entity_id, entity_type) -> (str, str):
    """
    Returns the sources for an entity_id and entity_type
    :param entity_id: entity id
    :param entity_type: entity type
    :return: (MeSH, URI Link) | FID | NCBI Gene | NCBI Taxonomy
    """
    entity_id_str = str(entity_id).lower()
    if entity_id_str.startswith('mesh'):
        return "MeSH", "https://meshb.nlm.nih.gov/record/ui?ui="
    if entity_id_str.startswith('fid'):
        return "FID", None
    if entity_id_str.startswith('q'):
        return "Wikidata", "https://www.wikidata.org/wiki/"
    if entity_id_str.startswith('db'):
        return "DrugBank", "https://go.drugbank.com/drugs/"
    if entity_id_str.startswith('chembl'):
        return "ChEMBL", "https://www.ebi.ac.uk/chembl/compound_report_card/"
    if entity_type == PLANT_FAMILY_GENUS:
        return "Plant Family Database", None
    if entity_type == EXCIPIENT:
        return "Excipient Database", None
    if entity_type == GENE:
        return "NCBI Gene", "https://www.ncbi.nlm.nih.gov/gene/"
    if entity_type == SPECIES:
        return "NCBI Taxonomy", "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="
    if entity_type in DALL:
        return "Own Vocabularies", None
    raise KeyError('Do not not know the source for entity: {} {}'.format(entity_id, entity_type))


DOSAGE_FORM = "DosageForm"
DRUG = "Drug"
CHEMICAL = "Chemical"
MUTATION = "Mutation"
GENE = "Gene"
SPECIES = "Species"
DISEASE = "Disease"
VARIANT = "Variant"
CELLLINE = "CellLine"
SNP = "SNP"
PROTEINMUTATION = "ProteinMutation"
DNAMUTATION = "DNAMutation"
DOMAINMOTIF = "DomainMotif"
GENUS = "Genus"
STRAIN = "Strain"
EXCIPIENT = "Excipient"
PLANT_FAMILY_GENUS = "PlantFamily/Genus"
CHEMBL_CHEMICAL = "Chemical"
METHOD = "Method"
LAB_METHOD = "LabMethod"
VACCINE = "Vaccine"
HEALTH_STATUS = "HealthStatus"
TARGET = "Target"
ORGANISM = "Organism"
TISSUE = "Tissue"

ALL = {
    DOSAGE_FORM,
    DRUG,
    CHEMICAL,
    MUTATION,
    GENE,
    SPECIES,
    DISEASE,
    VARIANT,
    CELLLINE,
    SNP,
    PROTEINMUTATION,
    DNAMUTATION,
    DOMAINMOTIF,
    EXCIPIENT,
    PLANT_FAMILY_GENUS,
    CHEMBL_CHEMICAL,
    METHOD,
    LAB_METHOD,
    VACCINE,
    HEALTH_STATUS,
    TARGET,
    ORGANISM,
    TISSUE
}

DALL = {
    DOSAGE_FORM,
    DRUG,
    EXCIPIENT,
    PLANT_FAMILY_GENUS,
    CHEMBL_CHEMICAL,
    DISEASE,
    METHOD,
    LAB_METHOD,
    VACCINE,
    HEALTH_STATUS,
    ORGANISM,
    TISSUE,
    CELLLINE
}

# set of all tags which are supported by our taggers
ENT_TYPES_SUPPORTED_BY_TAGGERS = {
    DOSAGE_FORM,
    DRUG,
    EXCIPIENT,
    CHEMICAL,
    GENE,
    SPECIES,
    DISEASE,
    PLANT_FAMILY_GENUS,
    CHEMBL_CHEMICAL,
    METHOD,
    LAB_METHOD,
    VACCINE,
    HEALTH_STATUS,
    TARGET,
    ORGANISM,
    TISSUE,
    CELLLINE
}

TAG_TYPE_MAPPING = dict(
    DF=DOSAGE_FORM,
    DR=DRUG,
    DC=CHEMBL_CHEMICAL,
    E=EXCIPIENT,
    PF=PLANT_FAMILY_GENUS,
    C=CHEMICAL,
    MU=MUTATION,
    G=GENE,
    S=SPECIES,
    D=DISEASE,
    V=VARIANT,
    CL=CELLLINE,
    M=METHOD,
    LM=LAB_METHOD,
    HS=HEALTH_STATUS,
    O=ORGANISM,
    TI=TISSUE,
    A="ALL",
    DA="DALL"
)

DICT_TAG_TYPES = {"DF", "DR", "DC", "E", "PF", "DA", "D", "M", "LM", "HS", "T", "O", "TI"}

ENTITY_TYPES = dict(
    Chemical=CHEMICAL,
    Disease=DISEASE,
    Drug=DRUG,
    Gene=GENE,
    Species=SPECIES,
    Mutation=MUTATION,
    CellLine=CELLLINE,
    Variant=VARIANT,
    ProteinMutation=PROTEINMUTATION,
    DNAMutation=DNAMUTATION,
    SNP=SNP,
    DosageForm=DOSAGE_FORM,
    DomainMotif=DOMAINMOTIF,
    Genus=GENUS,
    Strain=STRAIN,
    Excipient=EXCIPIENT,
    PlantFamily=PLANT_FAMILY_GENUS,
    DrugBankChemical=CHEMBL_CHEMICAL,
    Method=METHOD,
    LabMethod=LAB_METHOD,
    HealthStatus=HEALTH_STATUS,
    Target=TARGET,
    Organism=ORGANISM,
    Tissue=TISSUE
)
