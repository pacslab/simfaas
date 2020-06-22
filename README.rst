Serverless Performance Simulator
================================

|PyPI| |PyPI - Status| |Travis (.com)| |Libraries.io dependency status
for latest release| |GitHub|

This is a project done in `PACS Lab <https://pacs.eecs.yorku.ca/>`__
aiming to develop a performance simulator for serverless computing
platforms. Using this simulator, we can calculate Quality of Service
(QoS) metrics like average response time, average probability of cold
start, average running servers (directly reflecting average cost),
histogram of different events, distribution of number of servers
throughout time, and many other characteristics.

The developed performance model can be used to debug/improve analytical
performance models, try new and improved management schema, or dig up a
whole lot of properties of a common modern scale-per-request serverless
platforms.

Artifacts
---------

-  `PyPi Package <https://pypi.org/project/pacssim/>`__
-  `Github
   Repo <https://github.com/nimamahmoudi/serverless-performance-simulator>`__
-  `ReadTheDocs
   Documentation <https://serverless-performance-simulator.readthedocs.io/en/latest/>`__
-  `Examples <./examples>`__

Requirements
------------

-  Python 3.6 or above
-  PIP

Installation
------------

Install using pip:

.. code:: sh

   pip install pacssim

Upgrading using pip:

.. code:: sh

   pip install pacssim --upgrade

For installation in development mode:

.. code:: sh

   git clone https://github.com/nimamahmoudi/serverless-performance-simulator
   cd serverless-performance-simulator
   pip install -e .

Usage
-----

A simple usage of the serverless simulator is shown in the following:

.. code:: py

   from pacssim.ServerlessSimulator import ServerlessSimulator as Sim

   sim = Sim(arrival_rate=0.9, warm_service_rate=1/1.991, cold_service_rate=1/2.244,
               expiration_threshold=600, max_time=1e6)
   sim.generate_trace(debug_print=False, progress=True)
   sim.print_trace_results()

Which prints an output similar to the following:

::

   100%|██████████| 1000000/1000000 [00:42<00:00, 23410.45it/s]
   Cold Starts / total requests:    1213 / 898469
   Cold Start Probability:          0.0014
   Rejection / total requests:      0 / 898469
   Rejection Probability:           0.0000
   Average Instance Life Span:      6335.1337
   Average Server Count:            7.6612
   Average Running Count:           1.7879
   Average Idle Count:              5.8733

Using this information, you can predict the behaviour of your system in
production.

Development
-----------

In case you are interested in improving this work, you are always
welcome to open up a pull request. In case you need more details or
explanation, contact me.

To get up and running with the environment, run the following after
installing ``Anaconda``:

.. code:: sh

   conda env create -f environment.yml
   conda activate simenv
   pip install -r requirements.txt
   pip install -e .

After updating the README.md, use the following to update the README.rst
accordingly:

.. code:: sh

   bash .travis/readme_prep.sh

Examples
--------

Some of the possible use cases of the serverless performance simulator
are shown in the ``examples`` folder in our Github repository.

License
-------

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

Citation
--------

You can find the paper with details of the simultor in `PACS lab
website <https://pacs.eecs.yorku.ca/publications/>`__. You can use the
following bibtex entry for citing our work:

.. code:: bib

   Coming soon...

.. |PyPI| image:: https://img.shields.io/pypi/v/pacssim.svg
.. |PyPI - Status| image:: https://img.shields.io/pypi/status/pacssim.svg
.. |Travis (.com)| image:: https://img.shields.io/travis/com/nimamahmoudi/serverless-performance-simulator.svg
.. |Libraries.io dependency status for latest release| image:: https://img.shields.io/librariesio/release/pypi/pacssim.svg
.. |GitHub| image:: https://img.shields.io/github/license/nimamahmoudi/serverless-performance-simulator.svg

