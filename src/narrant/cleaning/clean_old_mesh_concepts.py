import argparse
import logging
from datetime import datetime

from sqlalchemy import or_

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag, Predication
from kgextractiontoolbox.progress import Progress
from narrant.config import MESH_SUPPLEMENTARY_FILE, MESH_DESCRIPTORS_FILE
from narrant.mesh.data import MeSHDB
from narrant.mesh.supplementary import MeSHDBSupplementary


def clean_old_mesh_concepts(force_deletion: bool):
    start = datetime.now()
    logging.info("Cleaning old mesh concepts [force deletion: {}]".format(force_deletion))

    supp = MeSHDBSupplementary()
    supp.load_xml(MESH_SUPPLEMENTARY_FILE, prefetch_all=True, verbose=True)

    desc = MeSHDB()
    desc.load_xml(MESH_DESCRIPTORS_FILE, prefetch_all=True, verbose=True)

    logging.info("Retrieve MeSH terms from tag table...")
    session = Session.get()
    query = session.query(Tag.ent_id)
    query = query.filter(Tag.ent_id.like('MESH:%'))
    query = query.distinct()

    old_mesh_terms = set()
    progress = Progress(query.count())
    progress.start_time()
    for idx, t in enumerate(query):
        entity_id = t.ent_id.split(":")[-1]
        is_supp = False
        is_desc = False

        # check each type separately
        try:
            supp.record_by_id(entity_id)
            is_supp = True
        except ValueError:
            pass
        try:
            desc.desc_by_id(entity_id)
            is_desc = True
        except ValueError:
            pass

        if is_supp or is_desc:
            old_mesh_terms.add(t)
        progress.print_progress(idx)
    progress.done()

    logging.info("Found {} old mesh terms:".format(len(old_mesh_terms)))
    print(old_mesh_terms)

    if not force_deletion:
        response = input("Do you want to delete all old mesh terms? [y/n]")
        response = response[0]
        if response.lower() != 'y':
            logging.info("Canceled deletion. Exiting...")
            return
    else:
        logging.info("Force deleting all old mesh terms")

    # delete old entities in the Tag-table
    query = session.query(Tag)
    query = query.filter(Tag.ent_id.in_(old_mesh_terms))
    logging.info(f"Deleting {query.count()} old mesh terms in Tag-table")
    query.delete(synchronize_session=False)
    session.commit()

    # delete old entities in the Relation-table
    query = session.query(Predication)
    query = query.filter(or_(Predication.subject_id.in_(old_mesh_terms), Predication.object_id.in_(old_mesh_terms)))
    logging.info(f"Deleted {query.count()} old mesh terms in Predication-table")
    query.delete(synchronize_session=False)
    session.commit()
    logging.info(f"Finished after {datetime.now() - start}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", help="Force deletion of old mesh DB entries")
    args = parser.parse_args()
    clean_old_mesh_concepts(args.force)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
    main()
