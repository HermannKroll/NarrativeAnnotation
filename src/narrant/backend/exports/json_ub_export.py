import argparse
import json
import logging

from kgextractiontoolbox.document.document import TaggedDocument
from kgextractiontoolbox.document.export import export
from narrant.entity.entityresolver import EntityResolver
from narrant.entitylinking import enttypes
from narrant.entitylinking.enttypes import get_entity_source


def write_doc_with_entity_source(doc: TaggedDocument, export_format: str, f, first_doc: bool, export_content=True,
                                 export_tags=True):
    """
    Writes a document to a file
    :param doc: the tagged document object
    :param export_format: the given export format
    :param f: the open file
    :param first_doc: true if its the first document
    :param export_content: content should be exported
    :param export_tags: tags should be exported
    :return: None
    """
    if export_format != "json":
        raise ValueError("only the JSON format is supported")
    if export_format == "json":
        if not first_doc:
            f.write(",\n")

        doc_dict = doc.to_dict(export_content=export_content, export_tags=export_tags)
        for t in doc_dict["tags"]:
            e_id, e_type = t["id"], t["type"]
            entity_resolver = EntityResolver()
            name = entity_resolver.get_name_for_var_ent_id(entity_id=e_id, entity_type=e_type)
            source, URI_source = get_entity_source(e_id, e_type)
            t["name"] = name
            t["source"] = source
            if URI_source:
                if 'MESH:' in e_id:
                    e_id = e_id.replace('MESH:', '')
                t["URI"] = f'{URI_source}{e_id}'
        json.dump(doc_dict, f, indent=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--ids", nargs="*", metavar="DOC_ID")
    parser.add_argument("--idfile", help='file containing document ids (one id per line)')
    parser.add_argument("-c", "--collection", help="Collection(s)", default=None)
    parser.add_argument("-d", "--document", action="store_true", help="Export content of document")
    parser.add_argument("--translate_ids", help="force the translation of document ids via DocumentTranslation",
                        required=False, action="store_true")
    parser.add_argument("--sqllog", action="store_true", help='logs sql commands')
    args = parser.parse_args()

    if args.ids and args.idfile:
        parser.error('Does not support a list of ids and an ids file')

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
    logger = logging.getLogger("export")
    if args.sqllog:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    tag_types = enttypes.ALL
    export_tags = True

    if args.ids:
        document_ids = [int(x) for x in args.ids]
    elif args.idfile:
        logger.info('reading id file: {}'.format(args.idfile))
        with open(args.idfile, 'r') as f:
            document_ids = list(set([int(line.strip()) for line in f]))
        logger.info('{} ids retrieved from id file..'.format(len(document_ids)))
    else:
        document_ids = None
    export(args.output, tag_types=tag_types, export_tags=export_tags,
           document_ids=document_ids, collection=args.collection, content=args.document, logger=logging,
           export_format="json", write_doc=write_doc_with_entity_source, translate_document_ids=args.translate_ids)
    logging.info('Finished')


if __name__ == "__main__":
    main()
