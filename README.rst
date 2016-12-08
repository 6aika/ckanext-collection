=============
ckanext-collection
=============

This extension provides functionality similar to CKAN core groups. This extension can be used to generate collections
of datasets when groups are used to implement some other functionality e.g. categories.

The extension creates a new route to '/collection' through where collections can be searched and managed. The extension
also creates a subnav into package read where the active package can be added into existing collections


------------
Requirements
------------

This extension is developed with CKAN version 2.6, but older 2.x versions should also work


------------
Installation
------------

To install ckanext-collection:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-collection Python package into your virtual environment::

     pip install ckanext-collection

3. Add ``collection`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


------------------------
Development Installation
------------------------

To install ckanext-collection for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/6aika/ckanext-collection.git
    cd ckanext-collection
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

TODO: No tests implemented yet
