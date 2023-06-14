mkdir data

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2023.gz
gzip -d desc2023.gz
mv desc2023 data/desc2023.xml

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2023.gz
gzip -d supp2023.gz
mv supp2023 data/supp2023.xml

wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
mv gene_info.gz data/gene_info_2023.gz
