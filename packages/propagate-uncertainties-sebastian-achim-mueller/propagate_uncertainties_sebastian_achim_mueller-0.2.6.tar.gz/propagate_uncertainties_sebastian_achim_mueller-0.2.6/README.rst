#######################
Propagate Uncertainties
#######################
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|

Propagate the uncertainties of your variables in simple expressions.

Examples
--------
.. code:: python

    import propagate_uncertainties as pu

    pu.add(x=1, x_au=0.1, y=4, y_au=0.1)
    (5, 0.14142135623730953)

    pu.multiply(x=2, x_au=0.2, y=3, y_au=0.1)
    (6, 0.632455532033676)

    pu.divide(x=5.0, x_au=1.0, y=2.0, y_au=0.1)
    (2.5, 0.5153882032022076)

    pu.sqrt(x=4, x_au=0.1)
    (2.0, 0.025)


Functions
---------
- ``add(x,y)``
- ``multiply(x,y)``
- ``divide(x,y)``
- ``hypot(x,y)``
- ``sqrt(x)``
- ``max([x0, x1, x2, ... xN])``
- ``sum([x0, x1, x2, ... xN])``
- ``sum_axis0(X)``
- ``integrate(f=[y0, y1, y2, ... yN], x_bin_edges=[x0, x1, x2, ... x(N+1)])``


.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/propagate_uncertainties/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/propagate_uncertainties/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/propagate_uncertainties_sebastian-achim-mueller
    :target: https://pypi.org/project/propagate_uncertainties_sebastian-achim-mueller

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
