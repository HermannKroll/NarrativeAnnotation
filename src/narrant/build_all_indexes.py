import logging
import json

from narrant.entity.drugbank2mesh import DrugBank2MeSHMapper
from narrant.entity.entityresolver import MeshResolver, GeneResolver, SpeciesResolver, DrugBankResolver
from narrant.entity.entitytagger import EntityTagger
from narrant.entity.genemapper import GeneMapper
from narrant.entity.meshontology import MeSHOntology
from narrant.config import BACKEND_CONFIG


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)
    with open(BACKEND_CONFIG) as f:
        config = json.load(f)
    print('Some indexes rely on the tag / predication table of the database...')
    is_sqlite = False or ("use_SQLite" in config and config["use_SQLite"])
    if is_sqlite:
        database_name = config["SQLite_path"]
    else:
        database_name = config["POSTGRES_DB"]
    print(f'Your current database is: {database_name}')
    user_input = input('Continue with database setting? (y/yes)')
    user_input = user_input.lower()
    if 'y' in user_input or 'yes' in user_input:
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('========== You should go and pick up some Coffee ===========')
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)

        logging.info('Building DrugBank2MeSHMapper....')
        drug2mesh = DrugBank2MeSHMapper()
        drug2mesh.compute_mappings()
        drug2mesh.store_index()

        logging.info('Computing entity ontology index...')
        entity_ontology = MeSHOntology.instance(load_index=False)
        entity_ontology.build_index_from_mesh()
        entity_ontology.store_index()

        logging.info('Computing Gene Mapping index...')
        gene_mapper = GeneMapper.instance(load_index=False)
        gene_mapper.build_gene_mapper_index()

        logging.info('Computing MeSH Resolver index...')
        mesh = MeshResolver()
        mesh.build_index()

        logging.info('Computing Gene Resolver index...')
        gene = GeneResolver()
        gene.build_index()

        logging.info('Computing Species Resolver index...')
        species = SpeciesResolver()
        species.build_index()

        logging.info('Computing DrugBank Resolver index...')
        drugbank = DrugBankResolver()
        drugbank.build_index()

        logging.info('Computing tagging index...')
        entity_tagger = EntityTagger.instance(load_index=False)
        entity_tagger.store_index()

        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('================= ! Finally ! You Did it ! =================')
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)
    else:
        print('user canceled index creation')


if __name__ == "__main__":
    main()