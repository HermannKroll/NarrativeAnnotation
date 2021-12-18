from narrant import config


class PlantFamilyVocabulary:

    @staticmethod
    def read_plant_family_vocabulary(plant_family_database=config.PLANT_FAMILTY_DATABASE_FILE,
                                     expand_terms=True):
        term_to_plant_family = {}
        with open(plant_family_database, 'rt') as f:
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
                    term_to_plant_family[term] = {plant_family.capitalize()}
        return term_to_plant_family