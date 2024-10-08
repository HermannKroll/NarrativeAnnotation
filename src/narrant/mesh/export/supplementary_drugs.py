import logging

from narrant.config import MESH_SUPPLEMENTARY_FILE, MESH_DESCRIPTORS_FILE
from narrant.mesh.data import MeSHDB
from narrant.mesh.supplementary import MeSHDBSupplementary


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    logging.info('load MeSH Supplementary file...')
    meshdb: MeSHDBSupplementary = MeSHDBSupplementary()
    meshdb.load_xml(MESH_SUPPLEMENTARY_FILE)

    relevant_records = []
    for record in meshdb.get_all_records():
        if record.note and ('drug ' in record.note.lower() and 'drug combination' not in record.note.lower()
                            and 'drug carrier' not in record.note.lower()):
            relevant_records.append(record)

    logging.info('load mesh file...')
    meshdb: MeSHDB = MeSHDB()
    meshdb.load_xml(MESH_DESCRIPTORS_FILE)

    for desc in meshdb.get_all_descs():
        for q in desc.allowable_qualifiers:
            if q.ui == 'Q000627':  # therapeutic usage
                relevant_records.append(desc)

    logging.info(f'exporting of {len(relevant_records)} records...')
    with open('mesh_drugs_2021.tsv', 'w') as f:
        f.write('MeSH Record\tHeading\tTerms\n')
        for d in relevant_records:
            # get all synonyms
            term_str = d.terms[0].string
            for t in d.terms[1:]:
                term_str += '; {}'.format(t.string)

            f.write('{}\t{}\t{}\n'.format(d.unique_id, d.name, term_str))

    logging.info('export finished')


if __name__ == "__main__":
    main()
