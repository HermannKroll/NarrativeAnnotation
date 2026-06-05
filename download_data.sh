mkdir data

#if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* || "$OSTYPE" == "freebsd" ]]; then
  wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2026.gz
  wget ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2026.gz
  wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
  wget https://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml
#elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
#  curl ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/desc2026.gz -o desc2026.gz
#  curl ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/xmlmesh/supp2026.gz -o supp2026.gz
#  curl ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz -o gene_info.gz
#  curl https://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml -o cellosaurus.xml
#fi

gzip -d desc2026.gz
mv desc2026 data/desc.xml

gzip -d supp2026.gz
mv supp2026 data/supp.xml

mv gene_info.gz data/gene_info.gz

mv cellosaurus.xml data/cellosaurus.xml
