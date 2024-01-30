import logging

from narrant.entity.entityresolver import EntityResolver
from narrant.entitylinking.enttypes import GENE, SPECIES


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    resolver = EntityResolver.instance()

    lines = []
    with open("entities.tsv", 'wt') as f:
        ent2name = [('MESH:', resolver.mesh.desc2heading),
                    (GENE, resolver.gene.geneid2name),
                    ('', resolver.chebml.chemblid2name),
                    (SPECIES, resolver.species.speciesid2name)]
        for prefix, e2name_dict in ent2name:
            for e_id, name in e2name_dict.items():
                if prefix == GENE:
                    name = name[0] + '//' + name[1]
                elif prefix == SPECIES:
                    new_name = []
                    if resolver.species.NAME_COMMON_SHORTCUT in name:
                        new_name.append(name[resolver.species.NAME_COMMON_SHORTCUT])
                    if resolver.species.NAME_SCIENTIFIC_SHORTCUT in name:
                        if new_name:
                            new_name.append('//')
                        new_name.append(name[resolver.species.NAME_SCIENTIFIC_SHORTCUT])
                    name = ''.join(new_name)

                lines.append(f'{prefix}{e_id}\t{name}')
        f.write('\n'.join([l for l in lines]))


if __name__ == '__main__':
    main()
