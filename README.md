wget http://download.freebase.com/datadumps/latest/browse/film.tar.bz2
tar -xvIf film.tar.bz2
python ./parse_tsv.py film > film.jsons

