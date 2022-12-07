import logging

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag
from narrant.entity.entityresolver import EntityResolver
from narrant.preprocessing.enttypes import TAG_TYPE_MAPPING, DALL

from sqlalchemy import func, desc
from argparse import ArgumentParser


def main(arguments=None):
    parser = ArgumentParser(description="Export top [limit(default=100)] tags from the database in csv format")

    parser.add_argument("-t", "--tag", choices=TAG_TYPE_MAPPING.keys(), nargs="+", default="DA")
    parser.add_argument("-c", "--collection", required=True)
    parser.add_argument("-l", "--limit", default=100, type=int)

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    args = parser.parse_args(arguments)
    ent_types = DALL if "DA" in args.tag else [TAG_TYPE_MAPPING[x] for x in args.tag]

    logging.info(f'Start extracting top 100 tags for entity-type(s) {ent_types} of collection {args.collection}')
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

        for tag in tags_query.all():
            name = EntityResolver.instance().get_name_for_var_ent_id(tag[1], tag[2])
            export_data.append(f'{tag[0]}\t{tag[1]}\t{name}\t{tag[3]}')

        logging.info('Writing data to file.')

        with open(f'top_{str(args.limit)}_tags_{args.collection}.csv', 'w') as file:
            file.write('\n'.join(export_data))
            file.close()
        logging.info('Write success. Finished!')
    except Exception as e:
        logging.error(f'An error occurred: {e}. Exiting.')

    finally:
        session.remove()


if __name__ == "__main__":
    main()
