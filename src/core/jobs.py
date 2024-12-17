from core.userdata_io import UserdataFile
"""Contains the default configuration of the basic application config."""


__default_jobs: dict[str, dict[str, dict | list]] = {}
"""
Jobs must be in the form:

{
    "job_name": [
        sources,  # list of sources
        destinations,  # list of destinations
        settings_file.data,
    ],
    ...
}
"""


job_file: UserdataFile = UserdataFile(filename='jobs', default_data=__default_jobs)
job_file.load()


# TODO Maybe add addition custom interface here for working with job files
