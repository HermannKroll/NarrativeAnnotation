import logging

from narrant.entity.entityresolver import EntityResolver

MESH_TO_EXPORT = ["MESH:D000090022",
                  "MESH:D000094504",
                  "MESH:D000092262",
                  "MESH:D000093667",
                  "MESH:D000092224",
                  "MESH:D000094408",
                  "MESH:D000092184",
                  "MESH:D000092165",
                  "MESH:D000095062",
                  "MESH:D000091942",
                  "MESH:D000093102",
                  "MESH:D000092522",
                  "MESH:D000093522",
                  "MESH:D000092945",
                  "MESH:D000093562",
                  "MESH:D000094382",
                  "MESH:D000094902",
                  "MESH:D000093485",
                  "MESH:D000093142",
                  "MESH:D000094562",
                  "MESH:D005135",
                  "MESH:D000092386",
                  "MESH:D000094443",
                  "MESH:D000094506",
                  "MESH:D000092723",
                  "MESH:D000092722",
                  "MESH:D000094463",
                  "MESH:D000094542",
                  "MESH:D000094182",
                  "MESH:D000092682",
                  "MESH:D000094682",
                  "MESH:D000092024",
                  "MESH:D000094422",
                  "MESH:D000092963",
                  "MESH:D000095025",
                  "MESH:D000092025",
                  "MESH:D000093182"]


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    resolver = EntityResolver.instance()

    with open('to_classify.tsv', 'wt') as f:
        f.write("Class\tDescriptor\tHeading\tURL")

        for mesh in MESH_TO_EXPORT:
            descriptor = mesh.split(":")[1]
            url = f'https://meshb.nlm.nih.gov/record/ui?ui={descriptor}'
            name = resolver.mesh.descriptor_to_heading(descriptor)
            f.write(f'\n\t{descriptor}\t{name}\t{url}')


if __name__ == '__main__':
    main()
