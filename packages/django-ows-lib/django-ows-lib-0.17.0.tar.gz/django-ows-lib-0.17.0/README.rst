.. image:: https://readthedocs.org/projects/django-ows-lib/badge/?version=latest
    :target: https://django-ows-lib.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/django-ows-lib.svg
    :target: https://pypi.org/project/django-ows-lib/
    :alt: PyPi version

.. image:: https://sonarcloud.io/api/project_badges/measure?project=mrmap-community_django-ows-lib&metric=coverage
    :target: https://sonarcloud.io/project/overview?id=mrmap-community_django-ows-lib
    :alt: Coverage

.. image:: https://sonarcloud.io/api/project_badges/measure?project=mrmap-community_django-ows-lib&metric=alert_status
    :target: https://sonarcloud.io/project/overview?id=mrmap-community_django-ows-lib
    :alt: Quality Gate



django-ows-lib
==============

Well layered ows lib with a client implementation to communicate with ogc services with django based objects, 
including xml mapper classes to serialize and deserialize ows xml files, such as capabilities.

Features
--------

* `WMS <https://www.ogc.org/standard/wms/>`_ client
* `WFS <https://www.ogc.org/standard/wfs/>`_ client
* `CSW <https://www.ogc.org/standard/cat/>`_ client


Quick-Start
-----------

Install it as any other django app to your project:

.. code-block:: bash

    $ pip install django-ows-lib

.. warning::
    As pre requirement you will need to install the `gdal and geos binaries <https://docs.djangoproject.com/en/4.2/ref/contrib/gis/install/geolibs/>`_ on your system first.
    
See the `documentation <https://django-ows-lib.readthedocs.io/en/latest/index.html>`_ for details.
