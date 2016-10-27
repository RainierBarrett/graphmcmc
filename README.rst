===============================
graphmcmc
===============================

.. image:: https://img.shields.io/travis/RainierBarrett/graphmcmc.svg
        :target: https://travis-ci.org/RainierBarrett/graphmcmc

.. image:: https://coveralls.io/repos/github/RainierBarrett/graphmcmc/badge.svg?branch=master
     :target: https://coveralls.io/github/RainierBarrett/graphmcmc?branch=master



This is a Markov-chain Monte Carlo simulator for graphs in Python. It takes into account total graph weights and path-lengths to the zero node to evaluate state transition probabilities. The proposal distribution I implement is as follows.

Each step I will propose a move thusly:
 1) Choose whether we cut or add an edge this step. P(add) = ( Nmax - Ni ) / ( Nmax - Nmin ). This way, we have a scaling probability of adding or subtracting an edge, and will always add when the edge count is minimal, and always cut when the edge count is maximal.
 2) Now choose a qualifying edge at random. In the case of addition, there are Nmax - Ni qualifying edges, leaving q( j|i ) = 1 / ( Nmax - Nmin ). In the case of cutting, there are Ni - Nbridges possible edges we could cut without disconnecting the graph, where Nbridges is the number of bridges in the graph at step i. Then in this case q( j|i ) = ( 1 / ( Ni - Nbridges ) ) * ( 1 - ( ( Nmax - Ni ) / ( Nmax -Nmin) ) ).


Running Unit Tests
--------
To run the unit tests for this program, make sure you have a suitable tox environment, then simply invoke the command "tox" from within the source directory. To test for coverage, run the command "coverage run --source=graphmcmc/graphmcmc.py setup.py test", and to check the coverage, run "coverage report -m". It's that easy!


Running the Program
--------
To run this program, simply change directories into the internal "graphmcmc" directory and run the command "python main.py". This will run a 10,000-step Monte-Carlo Markov Chain model, and report some statistics about the graphs visited throughout.

Note:Make SURE that you have included in the source directory a file with EXACT NAME "input.txt" or the program will not run. The input file should consist of nothing but lines of comma-separated pairs of floats, which indicate the 2-space coordinates of each node in the graph. *The top line will be treated as node zero.* In this implementation, due to time constraints, the graph is initialized as a minimal line graph (point 0 connects to point 1 only, point 1 to point 2 only, etc), but under the proposed distribution, the starting configuration should be mostly irrelevant in the long time limit. See the included "input.txt" for an example input file.

TODO:
--------
* Possibly re-implement to make a randomized initial graph.


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

