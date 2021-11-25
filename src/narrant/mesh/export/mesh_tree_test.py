from narrant.config import MESH_DESCRIPTORS_FILE
from narrant.mesh.data import MeSHDB


def main():
    db = MeSHDB.instance()
    db.load_xml(MESH_DESCRIPTORS_FILE)
    disease_str =  db.extract_disease_json()
    print(disease_str)
    with open('mesh_disease_tree.json', 'w+') as f:
        f.write(disease_str)

if __name__ == "__main__":
    main()