wget http://download.freebase.com/datadumps/latest/browse/film.tar.bz2
tar -xvIf film.tar.bz2
python ./parse_tsv.py film > film.jsons

easy_install elementtree

time pv film.jsons | ./jsons_to_changeset.py > film.cs.xml
