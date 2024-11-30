mkdir data

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2024.gz
gzip -d desc2024.gz
mv desc2024 data/desc.xml

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2024.gz
gzip -d supp2024.gz
mv supp2024 data/supp.xml

wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
mv gene_info.gz data/gene_info.gz

wget https://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml
mv cellosaurus.xml data/cellosaurus.xml
