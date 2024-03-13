import json
import logging
from argparse import ArgumentParser

from narrant.config import BACKEND_CONFIG
from narrant.entity.entityresolver import MeshResolver, GeneResolver, SpeciesResolver
from narrant.entity.genemapper import GeneMapper
from narrant.entity.meshontology import MeSHOntology


def build_entity_indexes(complete: bool, skip_mesh: bool, force: bool = False):
    logging.info('=' * 60)
    logging.info('=' * 60)
    logging.info('Building entity translation indexes...')
    if not complete:
        with open(BACKEND_CONFIG) as f:
            config = json.load(f)
        print('Some indexes rely on the tag table of the database...')
        is_sqlite = False or ("use_SQLite" in config and config["use_SQLite"])
        if is_sqlite:
            database_name = config["SQLite_path"]
        else:
            database_name = config["POSTGRES_DB"]
        print(f'Your current database is: {database_name}')
        if not force:
            user_input = input('Continue with database setting? (y/yes)')
            user_input = user_input.lower()
        else:
            user_input = 'y'
    else:
        user_input = 'y'
    if 'y' in user_input or 'yes' in user_input:
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('========== You should go and pick up some Coffee ===========')
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)

        if not skip_mesh:
            logging.info('Computing entity ontology index...')
            entity_ontology = MeSHOntology(load_index=False)
            entity_ontology.build_index_from_mesh()
            entity_ontology.store_index()

            logging.info('Computing MeSH Resolver index...')
            mesh = MeshResolver()
            mesh.build_index()
        else:
            logging.info('Skipping MeSH Index creation...')

        logging.info('Computing Gene Mapping index...')
        gene_mapper = GeneMapper(load_index=False)
        gene_mapper.build_gene_mapper_index()

        logging.info('Computing Gene Resolver index...')
        gene = GeneResolver()
        if complete:
            gene.build_index(query_db_gene_ids=False)
        else:
            gene.build_index()

        logging.info('Computing Species Resolver index...')
        species = SpeciesResolver()
        if complete:
            species.build_index(query_db_species_ids=False)
        else:
            species.build_index()

        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('================= ! Finally ! You Did it ! =================')
        logging.info('=' * 60)
        logging.info('=' * 60)
        logging.info('=' * 60)
    else:
        print('user canceled index creation')


def main():
    parser = ArgumentParser(description="Recreates Indexes")
    parser.add_argument("--force", action='store_true', help="Skip asking for the correct DB connection")
    parser.add_argument("--skip-mesh", action='store_true', help="Skip the recreation of MeSH Indexes")
    parser.add_argument("--complete", action='store_true', help="Builds a complete Gene and Species Index...")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    build_entity_indexes(args.complete, args.skip_mesh, force=args.force)


if __name__ == "__main__":
    main()
