Overview
========

This project contains a series of command-line tools for processing the [Freebase](http://www.freebase.com/)
[movie data](http://www.freebase.com/schema/film_ into a data set for use by the
[Discovery Engine](https://transparensee.com/docs/discovery/current/html/index.html).

Freebase data is available under the [creative commons attribution license](http://wiki.creativecommons.org/Creative_Commons_Attribution).
See [this page](http://www.freebase.com/policies/attribution) for example HTML you can include to if you use their data on your
web site.

Prerequisites
--------------

* Python 2.7 or newer
* An internet connection

1. To install the requisite python modules:

    ```sh
    easy_install elementtree # for facet_to_dimension.py, and json_to_tree_dimension.py
    easy_install google-api-python-client # for export_genres.py
    ```

1. Obtain the latest freebase film data dump and extract it locally

    ```sh
    wget http://download.freebase.com/datadumps/latest/browse/film.tar.bz2
    tar --bzip2 --extract --verbose --file film.tar.bz2
    ```

1. Process the film TSV files into a JSON intermediate form

    ```sh
    time ./parse_tsv.py film > film.jsons
    ```
1. Optionally filter out pornographic movies
    ```sh
    time pv film.jsons | ./jsons_filter.py > filtered.jsons
    ```

1. And then convert that into a Discovery Engine changeset. Note that if you do not have `pv` installed, use `cat`.
    ```sh
    time pv filtered.jsons | jsons_to_changeset.py | gzip -9 > changeset.xml.gz
    ```

1. Or you can do the three steps above in one fell swoop (using tee to retain copies of the intermediate output)

    ```sh
    time ./parse_tsv.py film | tee film.jsons | ./jsons_filter.py | tee filtered.jsons \
    | jsons_to_changeset.py | tee changeset.xml | gzip -9 > changeset.xml.gz
    ```

1. To export a keyword dimension to a tree dimension definition

    ```sh
    ./facet_to_dimension.py {keyword_dimension_id} {min_count_filter} | xmllint --format -
    ```

1. To export a tree structure of film genres based on a MQL query of the live freebase data
  1. Go to https://code.google.com/apis/console/
  1. Create a project
  1. Create a new server API key. You will use this below.
  1. Enable the freebase API for the project
  1. Retrieve the data using the API

    ```sh
    time ./export_genres.py API_KEY > genres.json
    ```

1. Convert the genre dump to an XML tree dimension for hand editing and inclusion in your dimensions.xml

    ```sh
    cat genres.json | ./json_to_tree_dimension.py| xmllint --format -
    ```

Feeling lazy?
-------------

Many of these files are available from our public s3 bucket [s3://t11e.datasets](http://t11e.datasets.s3.amazonaws.com/).
You can download a complete changeset [here](http://t11e.datasets.s3.amazonaws.com/freebase/film/2012-11-09/changeset.xml.gz).
