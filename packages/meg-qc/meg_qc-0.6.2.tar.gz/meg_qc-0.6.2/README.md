## MEGqc - a standardized pipeline for MEG data quality control

Magnetoencephalography (MEG) data are susceptible to noise and artifacts, which can severely corrupt the data quality. They can originate from environmental noise sources, e.g. powerline noise, internal noise sources like data contamination due to eye movements of the subject, or systemic noise sources, e.g. malfunction of a sensor or vibrations. For this reason, quality control of the data is an important step for valid and reproducible science (Niso et al., 2022). However, the visual detection and annotation of artifacts in MEG data require expertise, is a tedious and time extensive task, and hardly resembles a standardized procedure. Since quality control is commonly done manually it might also be subject to biases induced by the person inspecting the data. Despite the minimization of human biases, a standardized workflow for quality control will additionally make datasets better comparable thereby allowing for between-datasets comparisons as opposed to quality control within a single dataset. Hence, an automated and standardized approach to quality control is desirable for the quality assessment of in-house and shared datasets. To address this issue we developed a software tool for automated and standardized quality control of MEG recordings, MEGqc, which is inspired by software for quality control in the domain of fMRI, called mriqc (Esteban et al., 2017). 

MEGqc is designed to detect specific noise patterns in the data and visualize them in easily interpretable human-readable reports. Additionally, the calculated metrics are provided in machine-readable JSON files, which allow for better machine interoperability or integration into workflows. Among other measures we calculate the relative power of noise frequencies in the Power Spectral Density (PSD), several metrics to describe the ‘noisiness’ of channels and/or epochs, e.g. STD or peak-to-peak amplitudes, and quantification of EOG and ECG related noise averaged over all channels and on a per-channel basis (see the architecture UML for a list of all computed metrics). The software strives to help researchers to standardize and speed up their quality control workflow. This being said, usability is a central aspect of MEGqc. It requires only minimal user input to work: a path to the dataset and the tuning of a handful of parameters through a human and machine-readable configuration file, but can also be adapted to the specific needs of more experienced users by overriding the default values of respective parameters in the configuration file. However, this simple user interface, e.g. only one path to the dataset is required and the software will locate and load the files needed for the workflow, only works if the structural organization of the dataset is internally known to the software. 

Since neuroimaging data can be very diverse concerning their structural organization the software is tailored to the BIDS standard (Gorgolewski et al., 2016; Niso et al., 2018). Thus MEGqc requires the data to be organized according to BIDS. 

MEGqc strongly relies on the MNE-python software package (Gramfort et al., 2013).

Documentation, Installation Guide and Tutorial: https://ancplaboldenburg.github.io/megqc_documentation/index.html

The following derivatives are produced as the result of the analysis for each data file (.fif):

- HTML report for all metrics presented as interactive figures, that can be scrolled through and enlarged;
- TSV file with the results of the analysis for some of the metrics;
- machine-readable JSON file with the results of the analysis for all metrics.

### Between sample analysis

The package includes a small utility to compare quality metrics between
datasets. Assuming you have the per-sample TSV tables created by the MEGqc
pipeline, run::

    python -m meg_qc.calculation.between_sample_analysis \
        --tsv sample1/group_metrics.tsv sample2/group_metrics.tsv \
        --names sample1 sample2 \
        --output-dir results

All violin plots and regression results will be written to the ``results``
directory. Significant regression coefficients are marked with asterisks.

To add a mutual information (MI) analysis, include the ``--mi`` flag. The
number of permutations for the significance test is controlled via
``--mi-permutations`` (use ``0`` to disable permutation testing). For example::

    python -m meg_qc.calculation.between_sample_analysis \
        --tsv sample1/group_metrics.tsv sample2/group_metrics.tsv \
        --names sample1 sample2 \
        --output-dir results \
        --mi --mi-permutations 1000

MI results (raw, net, z-scores, p-values, normalized variants and entropies)
are stored in the ``mutual_information`` folder for each sample and for the
combined dataset.
