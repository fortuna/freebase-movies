wget http://download.freebase.com/datadumps/latest/browse/film.tar.bz2
tar -xvIf film.tar.bz2
python ./parse_tsv.py film > film.jsons

easy_install elementtree

time pv film.jsons | ./jsons_to_changeset.py > film.cs.xml

# Or in one fell swoop:

time ./parse_tsv.py film | tee film.jsons | ./jsons_to_changeset.py | tee film.cs.xml | gzip -9 > film.cs.xml.gz

# To export a keyword dimension to a tree dimension definition
./facet_to_dimension.py {keyword_dimension_id} {min_count_filter} | xmllint --format -

# To export a tree structure of film genres
# Go to https://code.google.com/apis/console/
# Create a project
# Create a new server API key. You will use this below.
# Enable the freebase API for the project

easy_install google-api-python-client
time ./export_genres.py API_KEY > genres.json

# To convert the genre dump to an XML tree dimension

cat genres.json | ./json_to_tree_dimension.py| xmllint --format -
