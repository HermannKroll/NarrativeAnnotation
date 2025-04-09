mkdir data

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2025.gz
gzip -d desc2025.gz
mv desc2025 data/desc.xml

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2025.gz
gzip -d supp2025.gz
mv supp2025 data/supp.xml

wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
mv gene_info.gz data/gene_info.gz

wget https://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml
mv cellosaurus.xml data/cellosaurus.xml
