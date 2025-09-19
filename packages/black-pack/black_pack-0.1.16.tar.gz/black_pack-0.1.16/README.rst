##########
black-pack
##########
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|


|BlackPackLogo|

|BlackPackStyle|

Linting and structural checking for python-packages.
Black-pack helps you to organize your python-package.
Black-pack is very basic and not meant to support custom structures.
Black-pack only checks if a python-package has a specific structure which the author thinks is 'reasonable practice' and which is now backed into black-pack.
Black-pack is meant to help you keep your various python-packages in 'reasonable' shape with ease.
The name 'black-pack' is becasue black-pack adopts parts of the mindset found in 'black'.

*******
Install
*******

.. code-block::

    pip install black_pack


*********************
Usage on command-line
*********************


Check
=====

.. code-block::

    black-pack check /path/to/my/python-package


Black-pack will print a list of errors to stdout when your package differs from black-pack's backed in expectations.


Init
====

.. code-block::

    black-pack init /path/to/my/new/python-package


Will write an entire skeleton for your python-package (All directories and files). You can pass optional arguments to e.g. specify the package's name.


Write
=====

.. code-block::

    black-pack write /path/to/my/python-package .gitignore


Writes a single specific file, e.g. the ``.gitignore``.


.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/black_pack/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/black_pack/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/black_pack
    :target: https://pypi.org/project/black_pack

.. |BlackPackLogo| image:: https://github.com/cherenkov-plenoscope/black_pack/blob/main/readme/black_pack.svg?raw=True

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
