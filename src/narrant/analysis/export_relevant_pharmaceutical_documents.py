import argparse
import logging

from sqlalchemy import func

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("idfile", help="Document ID file (documents must be in database)")
    parser.add_argument("-c", "--collection", required=True, help="Document collection")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    collection = args.collection

    logging.info('Querying relevant document ids...')
    session = Session.get()
    # subquery_drug = session.query(Tag.document_id).filter(and_(Tag.document_collection == collection,
    #                                                           Tag.ent_type.in_(
    #                                                               [DRUG, PLANT_FAMILY_GENUS]))).distinct()

    # subquery_pharm = session.query(DocumentClassification.document_id).filter(
    #    and_(DocumentClassification.document_collection == collection,
    #         DocumentClassification.classification.in_(['LitCovid', 'LongCovid', 'Pharmaceutical']))).distinct()

    # query = session.query(Document.id).filter(Document.collection == collection).filter(
    #    or_(Document.id.in_(subquery_drug),
    #        Document.id.in_(subquery_pharm)))

    query = session.query(Tag.document_id).filter(Tag.document_collection == collection).group_by(
        Tag.document_id).having(func.count(Tag.document_id) > 1)

    logging.info('Collecting document ids...')
    document_ids = set()
    for r in query:
        document_ids.add(int(r[0]))

    logging.info(f'Writing {len(document_ids)} to file {args.idfile}...')
    with open(args.idfile, 'wt') as f:
        f.write('\n'.join([str(d) for d in document_ids]))
    logging.info('Finished')


if __name__ == "__main__":
    main()
