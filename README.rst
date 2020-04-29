
.. image:: https://travis-ci.org/DataShades/ckanext-or_facet.svg?branch=master
    :target: https://travis-ci.org/DataShades/ckanext-or_facet

.. image:: https://codecov.io/gh/DataShades/ckanext-or_facet/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/DataShades/ckanext-or_facet

================
ckanext-or_facet
================

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!

------------
Installation
------------

To install ckanext-or-facet:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-or_facet Python package into your virtual environment::

     pip install ckanext-or-facet

3. Add ``or_facet`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # List of facets that are using OR when applied.
    # (optional, default: empty list).
    or_facet.facets = tags res_format


------------------------
Development Installation
------------------------

To install ckanext-or_facet for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/DataShades/ckanext-or_facet.git
    cd ckanext-or_facet
    python setup.py develop


-----------------
Running the Tests
-----------------

To run the tests, do::

  pytest --ckan-ini test.ini
