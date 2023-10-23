import logging
from argparse import ArgumentParser

from sqlalchemy import func, desc

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag
from narrant.entity.entityresolver import EntityResolver
from narrant.preprocessing.enttypes import TAG_TYPE_MAPPING, DALL


def main(arguments=None):
    parser = ArgumentParser(description="Export top [limit(default=100)] tags from the database in tsv format")

    parser.add_argument("-t", "--tag", choices=TAG_TYPE_MAPPING.keys(), nargs="+", default="DA")
    parser.add_argument("-c", "--collection", required=True)
    parser.add_argument("-l", "--limit", default=100, type=int)

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    args = parser.parse_args(arguments)
    ent_types = DALL if "DA" in args.tag else [TAG_TYPE_MAPPING[x] for x in args.tag]

    logging.info('Start extracting top {} tags for entity-type(s) {} of collection {}'
                 .format(args.limit, ent_types, args.collection))
    session = Session.get()

    try:
        tags_query = session.query(func.count(Tag.ent_str), Tag.ent_id, Tag.ent_type, Tag.ent_str)
        tags_query = tags_query.filter(Tag.document_collection == args.collection)
        tags_query = tags_query.filter(Tag.ent_type.in_(ent_types))
        tags_query = tags_query.group_by(Tag.ent_str)
        tags_query = tags_query.order_by(desc(func.count(Tag.ent_str)))
        tags_query = tags_query.limit(args.limit)

        logging.info('Extraction success. Generating data.')

        # count, entity id, name, tagged mention
        export_data = list()
        export_data.append('count\tentity id\tname\ttagged mention')

        for count, ent_id, ent_type, ent_str in tags_query.all():
            try:
                name = EntityResolver.instance().get_name_for_var_ent_id(ent_id, ent_type)
                export_data.append(f'{count}\t{ent_id}\t{name}\t{ent_str}')
            except Exception as e:
                logging.error("Exception \"{}\" occurred while resolving id {} \"{}\""
                              .format(e, ent_id, ent_str))

        logging.info('Writing data to file.')

        with open(f'top_{str(args.limit)}_tags_{args.collection.lower()}.tsv', 'w') as file:
            file.write('\n'.join(export_data))
            file.close()
        logging.info('Write success. Finished!')
    except Exception as e:
        logging.error(f'An error occurred: {e}. Exiting.')

    finally:
        session.remove()


if __name__ == "__main__":
    main()
