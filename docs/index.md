Welcome to Serverless Performance Simulator's documentation!
============================================================

[![dockeri.co](https://dockeri.co/image/nimamahmoudi/jupyter-simfaas)](https://hub.docker.com/r/nimamahmoudi/jupyter-simfaas)

This is a project done in [PACS Lab](https://pacs.eecs.yorku.ca/) aiming to develop a performance simulator for serverless computing platforms. Using this simulator, we can calculate Quality of Service (QoS) metrics like average response time, the average probability of cold start, average running servers (directly reflecting average cost), a histogram of different events, distribution of the number of servers throughout time, and many other characteristics.

The developed performance model can be used to debug/improve analytical performance models, try new and improved management schema, or dig up a whole lot of properties of a common modern scale-per-request serverless platform.

You can check out the source code in our [Github Repository](https://github.com/pacslab/simfaas). You can find the paper with details of the simultor in [PACS lab website](https://pacs.eecs.yorku.ca/publications/). You can use the following bibtex entry for citing our work:

```bib
@inproceedings{mahmoudi2021simfaas,
  author={Mahmoudi, Nima and Khazaei, Hamzeh},
  title={{SimFaaS: A Performance Simulator for Serverless Computing Platforms}},
  year={2021},
  publisher = {Springer},
  booktitle={{International Conference on Cloud Computing and Services Science}},
  pages={1--11},
  numpages = {11},
  keywords = {performance modelling, serverless computing, serverless, simulator, performance},
  series = {CLOSER '21},
  url_paper={},
  url_pdf={https://pacs.eecs.yorku.ca/pubs/pdf/SimFaaS_CLOSER2021_Website_Preprint.pdf}
}

@misc{mahmoudi2021simfaaspre,
  title={{SimFaaS: A Performance Simulator for Serverless Computing Platforms}},
  author={Nima Mahmoudi and Hamzeh Khazaei},
  year={2021},
  eprint={2102.08904},
  archivePrefix={arXiv},
  primaryClass={cs.DC},
  url_paper={https://arxiv.org/abs/2102.08904}
}
```

```eval_rst
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation.md
   sim.md
   temp-sim.md
   parsim.md
   simprocess.md
   api-reference.md
   jupyter-docker.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
