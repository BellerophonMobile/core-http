CORE HTTP Daemon
================

This is an initial prototype for a RESTful [CORE][core] API.  See the
[ideas][ideas] document for motivation/thoughts.

The implementation is very rough right now, and currently supports limited
creating of sessions and objects.

[core]: http://cs.itd.nrl.navy.mil/work/core/
[ideas]: https://docs.google.com/document/pub?id=1yxTdJyRzFN4GN6EWKDlHwelWxxcSuVFmCoRsvC0c-lk

Requirements
------------

* CORE should be installed to a location on PYTHONPATH
* Requires [CherryPy][cherrypy] 3.2 (tested with 3.2.2)
* Tested with Python 2.7.3

[cherrypy]: http://www.cherrypy.org/
