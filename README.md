# Astronomy

This contains various astronomy scripts I've written for my data analysis and processing.
Some of them may be more widely useful.
However, I provide no guarantee that they will even run, much less provide useable results.

If you use these scripts or derivates of them in support of data reduction, analysis, or publications, I would appreciate a mention in the acknowledgements as well as a (digital) copy of the paper.

## Directories

* `Archives/`		Pulling data from online archives
* `DataAnalysis/`		assist with processing/analysis of reduced data
* `DataReduction/`		data reduction scripts (often pipelines)
* `General/`		general use files, other scripts may depend on files in here
* `Observing/`		scripts related to observation planning and execution.
* --`PaperTools/`--			Paper writing and bibliography management tools. This now [its own repo](https://github.com/privong/PaperTools)
* --`SimulationTools/`--	Scripts related to analyzing outputs of simulations. This is now [its own repo](https://github.com/privong/SimulationTools). Currently this includes the Zeno N-body/SPH code (http://www.ifa.hawaii.edu/faculty/barnes/zeno/).
* `Talks/`			Tools to assist with managing talks written in LaTeX/beamer.

## Dependencies

Scripts in this repo may require one or more of:

* numpy
* scipy
* [astropy](http://www.astropy.org)
* matplotlib
* [ads](https://github.com/andycasey/ads)
* PyPDF2
* bibtexparser
* pycurl

As of 09 July 2015, most of these scripts were developed/tested in python 2.7.x, but written in a way that _should_ be python3 compatible, but that compatibility has not always been tested.
Moving forward, I will be using python3 exclusively (subject to availability of necessary libraries).
