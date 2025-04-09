import logging

from kgextractiontoolbox.backend.database import Session
from narrant.config import SQL_CLEANING_TAG


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
    logging.info('Invoking Tag SQL cleaning...')
    session = Session.get()
    with open(SQL_CLEANING_TAG, 'rt') as f:
        content = f.read()
        logging.info('Executing cleaning sql statement...')
        # execute statement by statement
        for sql_stmt in content.split(';'):
            # skip empty lines
            if not sql_stmt.strip():
                continue
            session.execute(sql_stmt)
            session.commit()
    logging.info('Finished')


if __name__ == "__main__":
    main()
