gradientcobra v1.1.6
====================

.. image:: https://raw.githubusercontent.com/hassothea/gradientcobra/main/gradientcobra_logo.svg
  :width: 200
  :alt: Gradient COBRA Logo


|Python39|  |Python310| 

Introduction
------------

``Gradientcobra`` is ``python`` package implementation of Gradient COBRA method by `S. Has (2023) <https://jdssv.org/index.php/jdssv/article/view/70>`__, as well as other aggregation and kernel methods.  
When the loss function of is smooth enough, gradient descent algorithm can be used to efficiently estimate the bandwidth parameter of the model.

For more information, read the "**Documentation and Examples**" below.

Installation
------------

In your terminal, run the following command to download and install from PyPI:


``pip install gradientcobra``


Citation
--------

If you find ``gradientcobra`` helpful, please consider citing the following papaers:

-   S.\  Has (2023), `Gradient COBRA: A kernel-based consensual aggregation for regression <https://jdssv.org/index.php/jdssv/article/view/70>`__.

-   A.\  Fischer and M. Mougeot (2019), `Aggregation using input-output trade-off <https://www.sciencedirect.com/science/article/pii/S0378375818302349>`__.

-   G.\  Biau, A. Fischer, B. Guedj and J. D. Malley (2016), `COBRA: A combined regression strategy <https://doi.org/10.1016/j.jmva.2015.04.007>`__.


Documentation and Examples
--------------------------

For more information about the library:

- read: `gradientcobra documentation <https://hassothea.github.io/files/CodesPhD/gradientcobra_doc.html>`__.

Read more about aggregation and kernel methods, see:

- `GradientCOBRA documentation <https://hassothea.github.io/files/CodesPhD/gradientcobra.html>`__.


- `MixCOBRARegressor documentation <https://hassothea.github.io/files/CodesPhD/mixcobra.html>`__.


- `Kernel Smoother documentation <https://hassothea.github.io/files/CodesPhD/kernelsmoother.html>`__.


- `Super Learner documentation <https://hassothea.github.io/files/CodesPhD/superlearner.html>`__.

Dependencies
------------

-  Python 3.9+
-  numpy, scipy, scikit-learn, matplotlib, pandas, seaborn, plotly, tqdm

References
----------

-  S. Has (2023). A Gradient COBRA: A kernel-based consensual aggregation for regression. 
   Journal of Data Science, Statistics, and Visualisation, 3(2).
-  A.\  Fischer, M. Mougeot (2019). Aggregation using input-output trade-off. 
   Journal of Statistical Planning and Inference, 200.
-  G. Biau, A. Fischer, B. Guedj and J. D. Malley (2016), COBRA: A
   combined regression strategy, Journal of Multivariate Analysis.
-  M. Mojirsheibani (1999), Combining Classifiers via Discretization,
   Journal of the American Statistical Association.
-  M.\  J. Van der Laan, E. C. Polley, and A. E. Hubbard (2007). Super Learner. 
   Statistical Applications of Genetics and Molecular Biology, 6, article 25.
-  T.\  Hastie, R. Tibshirani, J. Friedman (2009). Kernel Smoothing Methods.
   The Elements of Statistical Learning. Springer Series in Statistics. Springer, New York, NY.
   
.. |Travis Status| image:: https://img.shields.io/travis/hassothea/gradientcobra.svg?branch=master
   :target: https://travis-ci.org/hassothea/gradientcobra

.. |Python39| image:: https://img.shields.io/badge/python-3.9-green.svg
   :target: https://pypi.python.org/pypi/gradientcobra

.. |Python310| image:: https://img.shields.io/badge/python-3.10-blue.svg
   :target: https://pypi.python.org/pypi/gradientcobra

.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/hassothea/gradientcobra.svg
   :target: https://codecov.io/gh/hassothea/gradientcobra
