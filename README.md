CORE HTTP Daemon
================

This is an initial prototype for a RESTful [CORE][1] API.  See the
[ideas][2] document for motivation/thoughts.

The implementation is very rough right now, and currently supports limited
creating of sessions and objects.

[1]: http://cs.itd.nrl.navy.mil/work/core/
[2]: https://docs.google.com/document/pub?id=1yxTdJyRzFN4GN6EWKDlHwelWxxcSuVFmCoRsvC0c-lk

Requirements
------------

* CORE should be installed to a location on PYTHONPATH
* Requires [CherryPy][3] 3.2 (tested with 3.2.2)
* Tested with Python 2.7.3
* Download [Ext JS][4] (tested with version 4.1) and put in "static/extjs".
    * I didn't want to commit all of extjs while developing (over 200MB), I'll
      probably add only the required extjs files when the UI gets closer to
      being ready.

[3]: http://www.cherrypy.org/
[4]: http://www.sencha.com/products/extjs/
