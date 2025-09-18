# from setuptools import setup, find_packages

# setup(
#     name='postprocessing_seismo_lib',
#     version='0.1.22',
#     packages=find_packages(),
#     install_requires=['jsonschema>=4.0.0','pandas','xmltodict'],
#     include_package_data=True,
#     package_data={
#         'postprocessing_seismo_lib': ['example_data/*'],
#     },
#     extras_require={
#         ':python_version<"3.7"': ['importlib_resources']
#     },
#     #scripts=['scripts/run_seismo_example.py'],
#     author='Ryan Tam',
#     author_email='rwtam@caltech.edu',
#     description='A library for building and parsing Seismology API message bodies.',
#     long_description=open('README.md').read(),
#     long_description_content_type='text/markdown',
#     project_urls={
#         'Documentation': 'https://pypi-postprocessing-seismic-data.readthedocs.io/en/latest/',
#         #'Source': 'https://scsngit.gps.caltech.edu/services',  # if public
#         'Log Issues': 'https://scsngit.gps.caltech.edu/services/postprocessing-library/-/issues',
#         # 'Bug Tracker': 'https://gitlab.com/rwtam/pypi-postprocessing-seismic/issues',  # optional
#     },
#     # url='https://scsngit.gps.caltech.edu/services',  # Optional
#     classifiers=[
#         'Programming Language :: Python :: 3',
#         'Operating System :: OS Independent',
#     ],
#     python_requires='>=3.10',
# )


# import tomllib
# from pathlib import Path
from setuptools import setup, find_packages

# def get_version():
#     pyproject = Path(__file__).parent / "pyproject.toml"
#     with pyproject.open("rb") as f:
#         data = tomllib.load(f)
#     return data["tool"]["bumpversion"]["current_version"]


setup(
    name='postprocessing_seismo_lib',
    version='0.1.61',
    packages=find_packages(),
    install_requires=[
        'jsonschema>=4.0.0',
        'pandas',
        'xmltodict'
    ],
    include_package_data=True,
    package_data={'postprocessing_seismo_lib': ['example_data/*']},
    extras_require={':python_version<"3.7"': ['importlib_resources']},
    author='Ryan Tam',
    author_email='rwtam@caltech.edu',
    description='A library for building and parsing Seismology API message bodies.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    project_urls={
        'Documentation': 'https://pypi-postprocessing-seismic-data.readthedocs.io/en/latest/',
        'Log Issues': 'https://scsngit.gps.caltech.edu/services/postprocessing-library/-/issues',
        'Seismo-Service': 'https://github.com/SCEDC/seismo-service',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)




# setup(
#     name='postprocessing_seismo_lib',
#     version=get_version(),
#     packages=find_packages(),
#     install_requires=[
#         'jsonschema>=4.0.0',
#         'pandas',
#         'xmltodict'
#     ],
#     include_package_data=True,
#     package_data={'postprocessing_seismo_lib': ['example_data/*']},
#     extras_require={':python_version<"3.7"': ['importlib_resources']},
#     author='Ryan Tam',
#     author_email='rwtam@caltech.edu',
#     description='A library for building and parsing Seismology API message bodies.',
#     long_description=open('README.md').read(),
#     long_description_content_type='text/markdown',
#     project_urls={
#         'Documentation': 'https://pypi-postprocessing-seismic-data.readthedocs.io/en/latest/',
#         'Log Issues': 'https://scsngit.gps.caltech.edu/services/postprocessing-library/-/issues',
#     },
#     classifiers=[
#         'Programming Language :: Python :: 3',
#         'Operating System :: OS Independent',
#     ],
#     python_requires='>=3.10',
# )

