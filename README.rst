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


---------------
Updating translations
---------------

To extract all translatable strings run this command in the plugin root directory::

    python setup.py extract_messages

After this the updated ckanext-collection.pot with the source language can be pushed to Transifex with the transifex client.
(Note that you need to set your transifex credentials into ~/.transifexrc before running the command)::

    tx push --source

Translate new strings in Transifex and pull them by running::

    # --force can be added if old translations can be overwritten by the ones fetched from transifex (this is usually the case)
    tx pull

Recompile translations (-f is needed to since Transifex will set the exported files as fuzzy)::

    python setup.py compile_catalog -f
