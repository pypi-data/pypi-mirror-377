### Unofficial inference wrapper around DPTech's UnipKa model

This repo provides a simple wrapper around Zheng and co's fantastic [UnipKa](https://pubs.acs.org/doi/10.1021/jacsau.4c00271) model. It refactors their [example notebook](https://www.bohrium.com/notebooks/38543442597) into a small python package. 

This repo provides:

- A macro and micro pKa calculator, including pH-adjusted free energies for each microstate
- A logD calculator following the methodology of [Rowan Sci](https://chemrxiv.org/engage/chemrxiv/article-details/68388349c1cb1ecda02ba65d), calculating the weighted average of logP values for each microstate. 
- A state penalty function, useful for calculating permeability of neutral species, also following the methodology of [Rowan Sci](https://chemrxiv.org/engage/chemrxiv/article-details/68388349c1cb1ecda02ba65d) and [Lawrenz and co](https://pubs.acs.org/doi/10.1021/acs.jcim.3c00150). 
- An aqueous solvation energy calculator that uses xTB and the ALPB implicit solvent model.
- A Kp,uu classifier built using Gsolv, logD and the state penalty as features.
- A Jupyter widget to visualise the microstate distributions across a range of pH values.

Please cite the corresponding authors if you use this wrapper in your work!

![](unipka.gif)

Install using `pip install unipka`


Please see `examples.ipynb` [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1JQXbARpmfol0R4hzGISONCS9prgH-NSq?usp=sharing) or the unit tests for example usage.


Performance on the SAMPL benchmarks (pKa prediction):

<img src="benchmarks/sampl_results.png">

Performance on logD benchmark:

<img src="benchmarks/logd_results.png" width="600">


Performance on Kpuu benchmark:

<img src="benchmarks/kpuu_results.png" width="600">

Performance on FreeSolv benchmark (solvation prediction):

<img src="benchmarks/solvation_results.png" width="600">




