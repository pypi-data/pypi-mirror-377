###################
DynamicSizeRecarray
###################
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|

A dynamic, appandable version of Numpy's ``recarray``. The goal is to have a
``recarray``-like-object which can be appended to in a transparent and
efficient way.

*******
install
*******

.. code:: bash

    pip install dynamicsizerecarray


*********
basic use
*********

Initialize an empty ``DynamicSizeRecarray`` with a ``dtype``.

.. code:: python

    import dynamicsizerecarray

    dra = dynamicsizerecarray.DynamicSizeRecarray(
        dtype=[("hour", "u1"), ("minute", "u1"), ("temperature", "f8")]
    )

    len(dra)
    0


Or initialize the ``DynamicSizeRecarray`` with an already existing ``recarray``.

.. code:: python

    import numpy

    rec = numpy.recarray(
        shape=1,
        dtype=[("hour", "u1"), ("minute", "u1"), ("temperature", "f8")],
    )
    rec["hour"][0] = 2
    rec["minute"][0] = 13
    rec["temperature"][0] = 20.123

    dra = dynamicsizerecarray.DynamicSizeRecarray(recarray=rec)

    len(dra)
    1


After initializing, the ``DynamicSizeRecarray`` can be appended to dynamically.
You can append a ``record``, i.e. a dict.

.. code:: python

    dra.append_record({"hour": 3, "minute": 53, "temperature": 22.434})

    len(dra)
    2


Or you can append another ``recarray``.

.. code:: python

    rec = numpy.recarray(
        shape=1,
        dtype=[("hour", "u1"), ("minute", "u1"), ("temperature", "f8")],
    )
    rec["hour"][0] = 13
    rec["minute"][0] = 41
    rec["temperature"][0] = 18.623

    dra.append_recarray(rec)

    len(dra)
    3

When the dynamic appending is done, the ``DynamicSizeRecarray`` can be exported
to a classic, and static ``recarray``.

.. code:: python

    final = dra.to_recarray()


Further the ``DynamicSizeRecarray`` provides the properties ``shape`` and
``dtype``, and also implements ``__gettitem__``, ``__setitem__``.

.. code:: python

    dra.shape                   # shape
    (3, )

    dra[0]                      # __gettitem__
    (2, 13, 20.123)

    dra[1] = (7, 25, 21.45)     # __setitem__

    len(dra)                    # __len__
    3

    dra.dtype                   # exposes the internal recarray's dtype
    dtype((numpy.record, [('hour', 'u1'), ('minute', 'u1'), ('temperature', '<f8')]))


*******
wording
*******

- ``record`` is a ``dict`` with keys (and values) matching the ``dtype`` of the ``DynamicSizeRecarray``. (Wording is adopted from ``pandas``).

- ``records`` is just a ``list`` of ``record`` s (Also adopted from ``pandas``).

- ``recarray`` is short for ``np.recarray``.


.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/dynamicsizerecarray/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/dynamicsizerecarray/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/dynamicsizerecarray
    :target: https://pypi.org/project/dynamicsizerecarray

.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
