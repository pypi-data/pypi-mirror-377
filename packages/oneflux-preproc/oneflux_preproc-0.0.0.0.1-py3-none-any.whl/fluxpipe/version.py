version_name = "fluxpipe"
__name__ = version_name.lower().strip().replace(' ', '_')
version_number = "V0.0.0.0.3"
__version__ = version_number
full_version = version_number

release = 'dev' not in version_number and '+' not in version_number
short_version = version_number.split("+")[0]
