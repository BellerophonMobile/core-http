CORE HTTP Daemon
================

This is an initial prototype for a RESTful [CORE][core-home] API.  See the
[ideas][ideas-doc] document for motivation/thoughts.

The implementation is very rough right now, and currently supports limited
creating of sessions and objects.

[core-home]: http://cs.itd.nrl.navy.mil/work/core/
[ideas-doc]: https://docs.google.com/document/pub?id=1yxTdJyRzFN4GN6EWKDlHwelWxxcSuVFmCoRsvC0c-lk

Requirements
------------

* CORE should be installed to a location on PYTHONPATH
* Requires [CherryPy][cherrypy-home] 3.2 (tested with 3.2.2)
* Tested with Python 2.7.3
* Download [Ext JS][extjs-home] (tested with version 4.1) and put in
  "static/extjs".
    * I didn't want to commit all of extjs while developing (over 200MB), I'll
      probably add only the required extjs files when the UI gets closer to
      being ready.

[cherrypy-home]: http://www.cherrypy.org/
[extjs-home]: http://www.sencha.com/products/extjs/
