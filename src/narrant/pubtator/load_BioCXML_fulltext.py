import bioc
import logging
from datetime import datetime
from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import DocumentSection, Document
from argparse import ArgumentParser


def load_bioCXML_fulltexts_from_file(input_file: str, collection):
    """
        Loads the PubTator Central Bioc XML Dump to the database
        Extracts information for the tables: Document, DocumentSection
        :param input_file: path to the PubTator Central Bioc XML Dump file
        :param collection: the corresponding document collection
        :return: None
    """
    needed_information = ["paragraph", "fig_caption_title", "fig_caption", "table_caption"]
    session = Session.get()
    logging.info('Loading BioC XML file')
    reader = bioc.BioCXMLDocumentReader(input_file)
    doc_inserts = []
    doc_section_inserts = []
    temp_id = 0
    logging.info('Iterating through file')
    for document in reader:
        if document.passages:
            title = document.passages[0].text
            abstract = []
            sections = {}
            current_title = ""
            for idx, passage in enumerate(document.passages):
                if "type" in passage.infons and passage.infons["type"].startswith("title"):
                    if "type" in passage.infons and passage.infons["type"] == "title_1":
                        current_title = passage.text
                        sections[current_title] = ""
                    else:
                        if current_title != "":
                            sections[current_title] = sections[current_title] + ' ' + passage.text
                elif "type" in passage.infons and passage.infons["type"] in needed_information:
                    if current_title != "":
                        sections[current_title] = sections[current_title] + ' ' + passage.text
                if "type" in passage.infons and passage.infons["type"] == "abstract":
                    if passage.text.lower().startswith("citation"):
                        break  # skip citations
                    abstract.append(passage.text)
                # is it an abstract section title?
                elif "type" in passage.infons and passage.infons["type"] == "abstract_title_1":
                    if passage.text.lower().startswith("citation"):
                        break  # skip citations
                    abstract.append(passage.text)
            abstract = ' '.join(abstract)
            document_id = int(document.passages[0].infons['article-id_pmid'])
            if temp_id != document_id:
                doc_inserts.append(dict(id=document_id,
                                        collection=collection,
                                        title=title,
                                        abstract=abstract,
                                        date_inserted=datetime.now()))
            temp_id = document_id
            for i, key in enumerate(sections):
                '''
                if sections[key] == '':
                    continue
                '''
                doc_section_inserts.append(dict(document_id=document_id,
                                                document_collection=collection,
                                                position=i,
                                                title=key,
                                                text=sections[key]))
    logging.info('Inserting information')
    Document.bulk_insert_values_into_table(session, doc_inserts)
    DocumentSection.bulk_insert_values_into_table(session, doc_section_inserts)
    logging.info('Finished')


def main():
    parser = ArgumentParser()
    parser.add_argument("input", help="BioCXML file")
    parser.add_argument("-c", "--collection", required=True, help="Name of the document collection")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    load_bioCXML_fulltexts_from_file(args.input, args.collection)


if __name__ == "__main__":
    main()
