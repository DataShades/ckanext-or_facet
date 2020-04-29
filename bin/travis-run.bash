#!/bin/bash
set -e

pytest --ckan-ini=subdir/test.ini --cov=ckanext.or_facet ckanext/or_facet/tests
