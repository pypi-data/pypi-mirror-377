##########
Json-utils
##########
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|

*****
numpy
*****
Uses ``json_numpy`` for transparent ``loads`` and ``dumps`` of lists into numpy-arrayrs if the ``dtype`` is either purely int or float.

*****
trees
*****
Recursively read (or write) ``.json`` files in a tree of directories.

*****
lines
*****
JSON-lines or ``.jsonl`` is a powerful extension to the JSON-family.

.. code-block:: python

    import json_utils as ju

    with ju.lines.open("my-items.jsonl.gz", mode="w|gz") as jl:
        for i in range(100):
            jl.write({"number": i})

    with ju.lines.open("my-items.jsonl.gz", mode="r|gz") as jl:
        for obj in jl:
            print("item", obj["number"])


.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/json_utils/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/json_utils/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/json_utils_sebastian-achim-mueller
    :target: https://pypi.org/project/json_utils_sebastian-achim-mueller

.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
