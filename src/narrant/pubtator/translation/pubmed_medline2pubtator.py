import logging
import os
from argparse import ArgumentParser
from datetime import datetime

from lxml import etree

from narrant.backend.models import Document
from narrant.progress import print_progress_with_eta
from narrant.pubtator.document import TaggedDocument


def pubmed_medline_load_file(filename):
    """
    Process the XML file *filename* and only process the documents whose PMID is contained in *dm_pmids*.
    One file contains multiple documents.

    .. note::

       Some descriptors are artificial. Descriptors and Qualifiers are concatenated by an "_", e.g., D001 and Q001
       become D001_Q001.

    :param filename: Filename of XML file
    :param db_pmids: Set of PMIDs (int) to process
    :return: Dictionary PMID -> set(Descriptors)
    """
    with open(filename) as f:
        tree = etree.parse(f)

    pubmed_articles = []
    for article in tree.iterfind("PubmedArticle"):

        # Get PMID
        pmids = article.findall("./MedlineCitation/PMID")
        if len(pmids) > 1:
            logging.warning(f"PubMed citation has more than one PMID {pmids}")
            continue  # BAD

        pmid = int(pmids[0].text)

        # Get the Title
        titles = article.findall('./MedlineCitation/Article/ArticleTitle')
        if len(titles) > 1:
            logging.warning(f'PubMed citation {pmid} has more than one title - skipping')
            continue
        title = str(titles[0].text)

        # skip documents without title
        if not title:
            continue

        # Get the Abstract
        abstracts = article.findall('./MedlineCitation/Article/Abstract/AbstractText')
        if len(abstracts):
            abstract_texts = []
            for a in abstracts:
                if 'Label' in a.attrib:
                    abstract_texts.append(f'{a.attrib["Label"]}: {a.text}')
                else:
                    abstract_texts.append(str(a.text))
            abstract = ' '.join(abstract_texts)
        else:
            abstract = None

        pubmed_articles.append(TaggedDocument(id=pmid, title=title, abstract=abstract))
    return pubmed_articles


def pubmed_medline_load_files(directory, output):
    """
    Process a directory containg XML files. Only process those whose PMID is in *db_pmids*.
    Return a mapping from Descriptor to PMID

    :param directory:
    :param db_pmids:
    :return:
    """
    desc_to_pmids = {}

    files = [os.path.join(directory, fn) for fn in os.listdir(directory) if fn.endswith(".xml")]

    start = datetime.now()
    with open(output, 'wt') as f:
        for idx, fn in enumerate(files):
            print_progress_with_eta("Processing PubMed Medline XML files", idx, len(files), start, 1)
            tagged_docs = pubmed_medline_load_file(fn)
            for doc in tagged_docs:
                f.write(Document.create_pubtator(doc.id, doc.title, doc.abstract) + '\n')

    return desc_to_pmids


def main():
    parser = ArgumentParser()
    parser.add_argument("input", help="PubMed Medline Directory containing all xml files")
    parser.add_argument("output", help="Output will be written in PubTator Format", metavar="FILE")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    logging.info(f'Converting the PubMed Medline to PubTator ({args.input} -> {args.output})')
    pubmed_medline_load_files(args.input, args.output)


if __name__ == "__main__":
    main()
