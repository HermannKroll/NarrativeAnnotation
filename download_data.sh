mkdir data

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2021.gz
gzip -d desc2021.gz
mv desc2021 data/desc2021.xml

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2021.gz
gzip -d supp2021.gz
mv supp2021 data/supp2021.xml

wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
mv gene_info.gz data/gene_info_2021.gz

wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz
gzip -d PMC-ids.csv.gz
mv PMC-ids.csv data/PMC-ids.csv