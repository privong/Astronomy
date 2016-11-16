# Astronomy

This contains various astronomy scripts I've written for my data analysis and processing.
Some of them may be more widely useful.
However, I provide no guarantee that they will even run, much less provide useable results.

If you use these scripts or derivates of them in support of data reduction, analysis, or publications, I would appreciate a mention in the acknowledgements as well as a (digital) copy of the paper.

## Directories

In the past, this repo was a monolithic collection of various astronomy tools.
At some point, I decided it made more sense for things to live in their own repos (so, if someone was only interested in simulations, they could download only the [SimulationTools](https://github.com/privong/SimulationTools) repo).
Not all of the directories have been farmed out into their own repos, but this will eventually happen.
For now, this repository will be maintained as a "single pull" option, including those other repositories as submodules.

* *ArchivesTools/*		Pulling data from online archives. This is now [its own repo](https://github.com/privong/ArchiveTools).
* `DataAnalysis/`		assist with processing/analysis of reduced data
* `DataReduction/`		data reduction scripts (often pipelines)
* `General/`		general use files, other scripts may depend on files in here
* *ObservingTools*		scripts related to observation planning and execution. This is now [its own repo](https://github.com/privong/ObservingTools).
* *PaperTools/*			Paper writing and bibliography management tools. This is now [its own repo](https://github.com/privong/PaperTools).
* *SimulationTools/*	Scripts related to analyzing outputs of simulations. This is now [its own repo](https://github.com/privong/SimulationTools). Currently this includes the Zeno N-body/SPH code (http://www.ifa.hawaii.edu/faculty/barnes/zeno/).
* *Talks/*			Tools to assist with managing talks written in LaTeX/beamer. This is now [its own repo](https://github.com/privong/TalkTools).

## Dependencies

Scripts in this repo may require one or more of:

* numpy
* scipy
* [astropy](http://www.astropy.org)
* matplotlib
* [ads](https://github.com/andycasey/ads)
* PyPDF2
* bibtexparser
* astroquery

As of 09 July 2015, most of these scripts were developed/tested in python 2.7.x, but written in a way that _should_ be python3 compatible, but that compatibility has not always been tested.
Moving forward, I will be using python3 exclusively (subject to availability of necessary libraries).
