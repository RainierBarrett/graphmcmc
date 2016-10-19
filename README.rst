===============================
graphmcmc
===============================

.. image:: https://img.shields.io/travis/RainierBarrett/graphmcmc.svg
        :target: https://travis-ci.org/RainierBarrett/graphmcmc

.. image:: https://coveralls.io/repos/github/RainierBarrett/graphmcmc/badge.svg?branch=master
     :target: https://coveralls.io/github/RainierBarrett/graphmcmc?branch=master



This is a Markov-chain Monte Carlo simulator for graphs in Python. It takes into account total graph weights and path-lengths to the zero node to evaluate state transition probabilities.






Features
--------

TODO:
--------
* Add initial graph maker function -- ensure it's connected
* Add function to test if graphs are connected
* Add funciton to propose new state from previous, and calculate q(i|j), q(j|i)
* Add function to calculate pi_i / pi_j


License
---------
.. image:: https://www.gnu.org/graphics/gplv3-127x51.png

This program is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

