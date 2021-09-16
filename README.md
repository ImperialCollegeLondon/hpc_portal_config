# HPC Portal Config

Configuration files for the Imperial College HPC Portal. The supported
software packages and resource configurations for the portal are
specified in `portal_config.yaml`. Additional scripts for use in
jobs run by the portal are provided in the `portal_scripts` directory.

## Adding New Software Packages

A new package will be considered for addition if it meets the below
criteria:
* It is a software of general interest used by a number of users
* It is available as a centrally installed package (available via
  `module load`) on the RCS cluster

To request the addition of a software, create an issue in this
repository. Requests will be considered and acted upon on as resources
for the project become available.

Alternatively you may author a pull request (PR) for a piece of
software. Please do create an issue beforehand to check that the
software is suitable. See the existing entries for software and the
configuration file reference section of the [portal documention][] for
guidance. Please bear in mind that integration with data repositories
and the provision of high quality metadata are key aspects of the HPC
Portal. This means any new software configuration should consider what
files and metadata to upload as part of a publication. An issue can be
used for discussion.

[portal documentation]: https://github.com/ImperialCollegeLondon/hpc_portal#configuration-file-reference
