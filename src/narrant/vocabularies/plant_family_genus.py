from narrant import config


class PlantFamilyGenusVocabulary:

    @staticmethod
    def read_plant_genus_database(plant_genus_database=config.PLANT_GENUS_DATABASE_FILE,
                                  expand_terms=True):
        plant_genera = {}
        with open(plant_genus_database, 'rt') as f:
            for line in f:
                plant_family = line.strip()
                plant_family_lower = plant_family.lower()
                if expand_terms:
                    plant_family_terms = [plant_family_lower]
                    if plant_family.endswith('a'):
                        plant_family_terms.extend([f'{plant_family_lower}e',
                                                   f'{plant_family_lower}s',  # for the stupid ones :)
                                                   f'{plant_family_lower}rum'])
                    if plant_family.endswith('ae'):
                        plant_family_terms.extend([plant_family_lower[:-1],
                                                   f'{plant_family_lower[:-1]}s',
                                                   f'{plant_family_lower}rum'])
                    if plant_family.endswith('us'):
                        plant_family_terms.extend([plant_family_lower[:-1],
                                                   f'{plant_family_lower[:-1]}um'])
                    if plant_family.endswith('um'):
                        plant_family_terms.extend([f'{plant_family_lower[:-2]}i',
                                                   f'{plant_family_lower}s',  # for the stupid ones :)
                                                   f'{plant_family_lower[:-2]}a',
                                                   f'{plant_family_lower[:-2]}orum'])
                else:
                    plant_family_terms = [plant_family_lower]
                for term in plant_family_terms:
                    plant_genera[term] = {plant_family.capitalize()}
        return plant_genera

    @staticmethod
    def read_wikidata_plant_families(plant_family_wikidata=config.PLANT_FAMILY_WIKIDATA_FILE):
        plant_families = set()
        with open(plant_family_wikidata, 'rt') as f:
            for line in f:
                line = line.strip().lower()
                plant_families.add(line.capitalize())
        return plant_families

    @staticmethod
    def read_plant_family_genus_vocabulary(plant_genus_database=config.PLANT_GENUS_DATABASE_FILE,
                                           plant_family_wikidata=config.PLANT_FAMILY_WIKIDATA_FILE,
                                           expand_terms=True):
        plant_genera = PlantFamilyGenusVocabulary.read_plant_genus_database(
            plant_genus_database=plant_genus_database,
            expand_terms=expand_terms)

        plant_families = PlantFamilyGenusVocabulary.read_wikidata_plant_families(
            plant_family_wikidata=plant_family_wikidata)

        term2desc = plant_genera
        for family in plant_families:
            term = family.lower()
            if term not in term2desc:
                term2desc[term] = {family}
            else:
                term2desc[term].add(family)
        return term2desc
