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

ALL = (
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
    VACCINE
)

DALL = {
    DOSAGE_FORM,
    DRUG,
    EXCIPIENT,
    PLANT_FAMILY_GENUS,
    CHEMBL_CHEMICAL,
    DISEASE,
    METHOD,
    LAB_METHOD,
    VACCINE
}

# set of all tags which are supported by our taggers
ENT_TYPES_SUPPORTED_BY_TAGGERS = (
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
    VACCINE
)

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
    A="ALL",
    DA="DALL"
)

DICT_TAG_TYPES = {"DF", "DR", "DC", "E", "PF", "DA", "D", "M", "LM"}

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
    LabMethod=LAB_METHOD
)
