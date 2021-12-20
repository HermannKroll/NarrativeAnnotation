mkdir data

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2022.gz
gzip -d desc2022.gz
mv desc2022 data/desc2022.xml

wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2022.gz
gzip -d supp2022.gz
mv supp2022 data/supp2022.xml

wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
mv gene_info.gz data/gene_info_2022.gz

wget ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz
gzip -d PMC-ids.csv.gz
mv PMC-ids.csv data/PMC-ids.csv