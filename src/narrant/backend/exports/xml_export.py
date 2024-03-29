import argparse
import logging
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag, DocumentTranslation
from kgextractiontoolbox.progress import print_progress_with_eta
from narrant.entity.entityresolver import EntityResolver
from narrant.entitylinking import enttypes
from narrant.entitylinking.enttypes import TAG_TYPE_MAPPING, get_entity_source

CONTENT_BUFFER_SIZE = 10000
TAG_BUFFER_SIZE = 100000


def export_xml(output_dir, tag_types, document_ids=None, collection=None, logger=None, translate_document_ids=False):
    """
    Exports a collection in the following structure:
    For each document create a xml file with: {document_id}.xml inside the output dir
    CA2995369.xml mit Inhalt
    <document>
        <tag source="MeSH">Obesity</tag>
        <tag source="MeSH">fumagillol</tag>
        <tag source="MeSH">trimethionine</tag>
    </document>
    :param output_dir: directory in which the xml files should be exported
    :param tag_types: set of tag types which should be exported
    :param document_ids: a set of document ids which should be exported, None means all documents of the collection
    :param collection: collection which should be exported , None means all collections
    :param logger: logging class which should be used
    :param translate_document_ids: if true, document ids will be translated back to their original ids
    :return:
    """
    logging.info("Beginning XML export...")
    if document_ids is None:
        document_ids = []
    else:
        logger.info('Using {} ids for a filter condition'.format(len(document_ids)))

    session = Session.get()

    doc_id_2_source_id = {}
    if translate_document_ids:
        logger.info('Querying DocumentTranslation source ids...')
        query = session.query(DocumentTranslation.document_id, DocumentTranslation.source_doc_id) \
            .filter(DocumentTranslation.document_collection == collection)
        for r in query:
            doc_id_2_source_id[r[0]] = r[1]
        logger.info(f'Found {len(doc_id_2_source_id)} id translations')

    logging.info('Counting documents...')
    if document_ids:
        document_count = len(document_ids)
    else:
        document_count = session.query(Tag.document_id.distinct()).filter_by(document_collection=collection).count()
    logger.info('{} documents found'.format(document_count))

    query = session.query(Tag.document_id, Tag.ent_id, Tag.ent_type).yield_per(TAG_BUFFER_SIZE)
    if collection:
        query = query.filter_by(document_collection=collection)
    if document_ids:
        query = query.filter(Tag.document_id.in_(document_ids))
    query = query.order_by(Tag.document_collection, Tag.document_id, Tag.id)

    if tag_types and enttypes.ALL != tag_types:
        query = query.filter(Tag.ent_type.in_(tag_types))

    entity_resolver = EntityResolver()
    tags_for_doc = defaultdict(set)
    translation_errors = 0
    missing_ent_ids = set()
    logging.info('Retrieving document tags...')
    start_time = datetime.now()
    for tag in query:
        doc_id, ent_id, ent_type = (tag.document_id, tag.ent_id, tag.ent_type)
        # collect tags for document (as long as tags are for the same document)
        tags_for_doc[doc_id].add((ent_id, ent_type))

    logging.info('Beginning export...')
    docs_exported = 0
    # export the tags for each document
    for doc_id, tags in tags_for_doc.items():
        docs_exported += 1
        print_progress_with_eta("exporting tags...", docs_exported, document_count, start_time, print_every_k=500)
        if not tags:
            continue
        if translate_document_ids:
            doc_id = doc_id_2_source_id[doc_id]
        else:
            doc_id = str(doc_id)
        filename = os.path.join(output_dir, "{}.xml".format(doc_id))
        with open(filename, 'w', encoding='utf-8') as f:
            top = Element('document')
            for e_id, e_type in tags:
                try:
                    entity_name = entity_resolver.get_name_for_var_ent_id(e_id, e_type)
                    entity_source, _ = get_entity_source(e_id, e_type)
                    if entity_source:
                        if '//' in entity_name:
                            for e_n in entity_name.split('//'):
                                tag = SubElement(top, "tag", dict(source=entity_source))
                                tag.text = e_n
                        else:
                            tag = SubElement(top, "tag", dict(source=entity_source))
                            tag.text = entity_name
                    else:
                        tag = SubElement(top, "tag")
                        tag.text = entity_name
                except KeyError:
                    missing_ent_ids.add((e_id, e_type))
                    continue
            # write the document
            xml_data = minidom.parseString(ET.tostring(top, encoding='utf-8')).toprettyxml(indent="   ")
            f.write(xml_data)

    if logger:
        logger.warning('the following entity ids are missing: {}'.format(missing_ent_ids))
        logger.warning('{} entity tags skips due to missing translations'.format(translation_errors))
        logger.info("tags of {} documents written to {}".format(docs_exported, output_dir))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    parser.add_argument("-c", "--collection", help="Collection")
    parser.add_argument("-p", "--patents", action="store_true",
                        help="Will replace the patent prefix ids by country codes")
    parser.add_argument("-t", "--tag", choices=TAG_TYPE_MAPPING.keys(), nargs="+", default="A")
    parser.add_argument("--sqllog", action="store_true", help='logs sql commands')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger("export")
    if args.sqllog:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    abs_path = os.path.abspath(args.output_dir)
    logging.info('exporting patents to: {}'.format(abs_path))
    if not os.path.isdir(args.output_dir):
        os.mkdir(abs_path)

    tag_types = []
    if args.tag:
        tag_types = enttypes.ALL if "A" in args.tag else [TAG_TYPE_MAPPING[x] for x in args.tag]

    export_xml(abs_path, tag_types, document_ids=None, collection=args.collection, logger=logger,
               translate_document_ids=args.patents)
    logging.info('Finished')


if __name__ == "__main__":
    main()
