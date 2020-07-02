Welcome to Serverless Performance Simulator's documentation!
============================================================

This is a project done in [PACS Lab](https://pacs.eecs.yorku.ca/) aiming to develop a performance simulator for serverless computing platforms. Using this simulator, we can calculate Quality of Service (QoS) metrics like average response time, the average probability of cold start, average running servers (directly reflecting average cost), a histogram of different events, distribution of the number of servers throughout time, and many other characteristics.

The developed performance model can be used to debug/improve analytical performance models, try new and improved management schema, or dig up a whole lot of properties of a common modern scale-per-request serverless platform.

You can check out the source code in our [Github Repository](https://github.com/pacslab/simfaas).

```eval_rst
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation.md
   sim.md
   temp-sim.md
   simprocess.md
   api-reference.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
