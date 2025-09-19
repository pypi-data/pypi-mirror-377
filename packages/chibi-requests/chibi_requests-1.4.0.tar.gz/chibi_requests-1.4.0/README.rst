==============
chibi_requests
==============


.. image:: https://img.shields.io/pypi/v/chibi_requests.svg
        :target: https://pypi.python.org/pypi/chibi_requests

.. image:: https://img.shields.io/travis/dem4ply/chibi_requests.svg
        :target: https://travis-ci.org/dem4ply/chibi_requests

.. image:: https://readthedocs.org/projects/chibi-requests/badge/?version=latest
        :target: https://chibi-requests.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




handle urls in a more easy and human way

* Free software: WTFPL
* Documentation: https://chibi-requests.readthedocs.io.


==========
how to use
==========


*********
Chibi_url
*********

.. code-block:: python

	from chibi_requests import Chibi_url

	url = Chibi_url( "http://ifconfig.me'" )
	response = url.get()
	assert response.status_code == 200
	assert response.is_text
	assert isinstance( response.native, str )

	response = url.post()
	assert response.status_code == 200
	assert response.json
	assert isinstance( response.native, dict )

	url = Chibi_url( "https://google.com" )
	url += "cosa/cosa2'
	assert "https://google.com/cosa/cosa2" == url
	url += "cosa3"
	assert "https://google.com/cosa/cosa2/cosa3" == url

	url = Chibi_url( "https://google.com" )
	url += { 'param1': 'value1', 'param2': 'value2' }
	assert url.parmas == { 'param1': 'value1', 'param2': 'value2' }

	url = Chibi_url( "https://google.com" )
	url += "?param1=value1"
	assert url.parmas == { 'param1': 'value1' }

	url = Chibi_url( "https://google.com" )
	assert url.host == 'google.com'
	assert url.schema == 'https'


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
