import logging

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag
from kgextractiontoolbox.progress import Progress
from narrant.entitylinking.enttypes import GENE


def clean_gene_ids_in_tag():
    """
    cleans the tag table by splitting and deleting gene entities containing ";"
    and inserts a list of cleaned gene_ids into the Tag table.
    :return: nothing
    """
    session = Session.get()
    logging.info('Counting the number of tags needed to be cleaned...')
    query = session.query(Tag)
    query = query.filter(Tag.ent_type == GENE)
    query = query.filter(Tag.ent_id.like('%;%'))
    tag_count = query.count()
    logging.info(f'{tag_count} tags found')
    insert_list = []
    progress = Progress(total=tag_count, text="Computing cleaning of gene_ids...")
    progress.start_time()
    for idx, tag_row in enumerate(query):
        progress.print_progress(idx)
        gene_ids = tag_row.ent_id.split(';')
        for gene_id in gene_ids:
            insert_list.append(dict(ent_type=tag_row.ent_type,
                                    start=tag_row.start,
                                    end=tag_row.end,
                                    ent_id=gene_id.strip(),
                                    ent_str=tag_row.ent_str,
                                    document_id=tag_row.document_id,
                                    document_collection=tag_row.document_collection))
    progress.done()
    logging.info(f"Inserting {len(insert_list)} cleaned gene_ids.")
    Tag.bulk_insert_values_into_table(session, insert_list)
    insert_list.clear()
    logging.info(f"Deleting {tag_count} old composed gene_ids.")
    query.delete(synchronize_session=False)
    session.commit()
    logging.info("Finished.")


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
    clean_gene_ids_in_tag()


if __name__ == "__main__":
    main()
