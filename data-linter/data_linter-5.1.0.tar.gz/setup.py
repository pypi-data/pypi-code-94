# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_linter', 'data_linter.validators']

package_data = \
{'': ['*'], 'data_linter': ['schemas/*']}

install_requires = \
['arrow-pd-parser>=0.4.1,<0.5.0',
 'boto3>=1.14.7,<2.0.0',
 'dataengineeringutils3>=1.0.1,<2.0.0',
 'iam_builder>=3.7.0,<4.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'mojap-metadata[arrow]>=1.1.1,<2.0.0',
 'pandas>=1.2,<2.0',
 'pyyaml>=5.3.1,<6.0.0']

extras_require = \
{'frictionless': ['frictionless==3.24.0'],
 'ge': ['great-expectations==0.12.9', 'awswrangler==2.3.0']}

entry_points = \
{'console_scripts': ['data_linter = data_linter.command_line:main']}

setup_kwargs = {
    'name': 'data-linter',
    'version': '5.1.0',
    'description': 'data linter',
    'long_description': '# Data Linter\n\nA python package to to allow automatic validation of data as part of a Data Engineering pipeline. It is designed to read in and validate tabular data against a given schema for the data. The schemas provided adhere to [our metadata schemas standards](https://github.com/moj-analytical-services/mojap-metadata/) for data. This package can also be used to manage movement of data from a landing area (s3 or locally) to a new location based on the result of the validation.\n\nThis package implements different validators using different packages based on the users preference:\n- `pandas`: (default) Uses our own lightweight pandas dataframe operations to run simple validation tests on the columns based on the datatype and additional tags in the metadata. Utilises pyarrow for reading data.\n- `frictionless`: Uses Frictionless data to validate the data against our metadata schemas. More information can be found [here](https://github.com/frictionlessdata/frictionless-py/)\n- `great-expectations`: Uses the Great Expectations data to validate the data against our metadata schemas. More information can be found [here](https://github.com/great-expectations/great_expectations)\n\n\n## Installation\n\n```bash\npip install data_linter # pandas validator only\n```\n\nOr to install the necessary dependencies for the non-default validators.\n\n```bash\npip install data_linter[frictionless] # To include packages required for the frictionless validator\n\n# OR\n\npip install data_linter[ge] # To include packages required for teh great-expectations validator\n```\n\n\n## Usage\n\nThis package takes a `yaml` based config file written by the user (see example below), and validates data in the specified s3 folder path against specified metadata. If the data conforms to the metadata, it is moved to the specified s3 folder path for the next step in the pipeline (note can also provide local paths for running locally). Any failed checks are passed to a separate location for testing. The package also generates logs to allow you to explore issues in more detail.\n\n### Simple Use\n\nTo run the validation, at most simple you can use the following:\n\n**In Python:**\n\n```python\nfrom data_linter.validation import run_validation\n\nconfig_path = "config.yaml"\n\nrun_validation(config_path)\n```\n\n**Via command line:**\n\n```bash\ndata_linter --config_path config.yaml\n```\n\n### Example config file\n\n```yaml\nland-base-path: s3://testing-bucket/land/  # Where to get the data from\nfail-base-path: s3://testing-bucket/fail/  # Where to write the data if failed\npass-base-path: s3://testing-bucket/pass/  # Where to write the data if passed\nlog-base-path: s3://testing-bucket/logs/  # Where to write logs\ncompress-data: true  # Compress data when moving elsewhere (only applicable from CSV/JSON)\nremove-tables-on-pass: true  # Delete the tables in land if validation passes\nall-must-pass: true  # Only move data if all tables have passed\nfail-unknown-files:\n    exceptions:\n        - additional_file.txt\n        - another_additional_file.txt\n\nvalidator-engine: pandas # will default to this if unspecified\n# (but other options are `frictionless` and `great-expectations`)\n\n# Tables to validate\ntables:\n    table1:\n        required: true  # Does the table have to exist\n        pattern: null  # Assumes file is called table1 (same as key)\n        metadata: meta_data/table1.json # local path to metadata\n\n    table2:\n        required: true\n        pattern: ^table2\n        metadata: meta_data/table2.json\n        row-limit: 10000 # for big tables - only take the first x rows\n```\n\nYou can also run the validator as part of a python script, where you might want to dynamically generate your config:\n\n```python\nfrom data_linter.validation import run_validation\n\nbase_config = {\n    "land-base-path": "s3://my-bucket/land/",\n    "fail-base-path": "s3://my-bucket/fail/",\n    "pass-base-path": "s3://my-bucket/pass/",\n    "log-base-path": "s3://my-bucket/log/",\n    "compress-data": False,\n    "remove-tables-on-pass": False,\n    "all-must-pass": False,\n    "validator-engine": "great-expectations",\n    "validator-engine-params": {"default_result_fmt": "BASIC", "ignore_missing_cols": True},\n    "tables": {}\n}\n\ndef get_table_config(table_name):\n    d = {\n        "required": False,\n        "expect-header": True,\n        "metadata": f"metadata/{table_name}.json",\n        "pattern": r"^{}\\.jsonl$".format(table_name),\n        "headers-ignore-case": True,\n        "only-test-cols-in-metadata": True # Only currently supported by great-expectations validator\n    }\n    return d\n\nfor table in ["table1", "table2"]:\n    base_config["tables"][table_name] = get_table_config(table_name)\n\nrun_validation(base_config) # Then watch that log go...\n```\n\n### Validating a single file\n\n> Without all the bells and whistles\n\nIf you do not need `data_linter` to match files to a specified config, log the process and then move data around based on the outcome of the validation you can just use the validators themselves:\n\n```python\n# Example using simple pandas validatior (without added data_linter features)\nimport json\nfrom data_linter.validators import PandasValidator\n\nfilepath = "tests/data/end_to_end1/land/table1.csv"\ntable_params = {\n    "expect-header": True\n}\nwith open("tests/data/end_to_end1/meta_data/table1.json") as f:\n    metadata = json.load(f)\n\npv = PandasValidator(filepath, table_params, metadata)\npv.read_data_and_validate()\n\npv.valid  # True (data in table1.csv is valid against metadata)\npv.response.get_result()  # Returns dict of all tests ran against data\n\n# The response object of for the PandasValidator in itself, and has it\'s own functions\npv.get_names_of_column_failures()  #\xa0[], i.e. no cols failed\n```\n\n\n### Parallel Running\n\nData Linter can also work in parallel to trigger multiple validations at once (only supports use of S3 atm). An example below:\n\nIn this scenario we use the parallisation process to init the process split the job into 4 validators and then run the closedown.\n\n- **The init stage** splits the config into 4 chunks, based on the file size of the data sitting in the specified land path. It split configs are written to a temporary path in S3 for each validator to pick up and run in parallel.\n- **The validator stage** can be ran in parallel (for simplicity they are run sequentially in the example below). Each validator will take the config in the temp folder path and process the files given in that subsetting config.\n- **The closedown stage** will take all the logs all validator runs, conbine them then move the data based on the validators results. It will then finally clean up the temp folder.\n\n```python\n# Simple example running DL with multiple validators (in this case 4)\n# [init] -> [validator]x4 -> [closedown]\nimport yaml\nfrom data_linter import validation\nfrom dataengineeringutils3.s3 import get_filepaths_from_s3_folder\n\n\nsimple_yaml_config = """\nland-base-path: s3://land/\nfail-base-path: s3://fail/\npass-base-path: s3://pass/\nlog-base-path: s3://log/\n\ncompress-data: false\nremove-tables-on-pass: true\nall-must-pass: true\n\n# Tables to validate\ntables:\n  table1:\n    required: true\n    metadata: tests/data/end_to_end1/meta_data/table1.json\n    expect-header: true\n\n  table2:\n    required: true\n    pattern: ^table2\n    metadata: tests/data/end_to_end1/meta_data/table2.json\n"""\n\ntest_folder = "tests/data/end_to_end1/land/"\nconfig = yaml.safe_load(simple_yaml_config)\n\n# Init stage\nvalidation.para_run_init(4, config)\n\n# Validation stage (although ran sequencially this can be ran in parallel)\nfor i in range(4):\n    validation.para_run_validation(i, config)\n\n# Closedown stage\nvalidation.para_collect_all_status(config)\nvalidation.para_collect_all_logs(config)\n```\n\n> There are more parallelisation examples, which can be found in the [test_simple_examples.py test module](tests/test_simple_examples.py)\n\n## Validators\n\n### Pandas\n\nTHis is the default validator used by data_linter as of the version 5 release.\n\n#### Dealing with timestamps and dates\n\nTimestamps are always a pain to deal with especially when using different file types. The Pandas Validator has tried to keep true to the file types based on the tests it runs.\n\nIf the file type stores date/timestamp information as a string (i.e. CSV and JSONL) then the pandas Validator will read in the timestamp / date columns as strings. It will then apply validation tests against those columns checking if the string representation of the dates in the data is a valid date. For timestamp and date types these tests assume ISO standard string representation `%Y-%m-%d %H:%M:%S` and `%Y-%m-%d`. If your timestamp/date types are comming in as strings that do not conform to the ISO standard format then you can provide you column in the metadata with a `datetime_format` property that specifies the exected format e.g.\n\n```json\n...\n"columns": [\n    {\n        "name": "date_in_uk",\n        "type": "date64",\n        "datetime_format": "%d/%m/%Y"\n    },\n...\n```\n\nOften you might recieve data that is exported from a system that might encode your timestamp as a date but is written to a format that encodes the data as a timestamp. In this scenario you would expect your dates (in a str timestamp format) to always have a time component of `00:00:00`. You can also use data_linter to validate this by specifing the datetime_format of your column as the expected timestamp in format but still specify that the data type is a date e.g.\n\n```json\n...\n"columns": [\n    {\n        "name": "date_in_uk",\n        "type": "date64",\n        "datetime_format": "%d/%m/%Y 00:00:00"\n    },\n...\n```\n\nIn the above data_linter will attempt to fist parse the column with the specified `datetime_format` and then as the column type is date it will check that it it truely a date (and not have a time component).\n\nIf the file_format is `parquet` then timestamps are encoded in the filetype and there are just read in as is. Currently data_linter doesn\'t support minimum and maximum tests for timestamps/dates and also does not currently have tests for time types. \n\n\n### Frictionless\n\nKnown errors / gotchas:\n- Frictionless will drop cols in a jsonl files if keys are not present in the first row (would recommend using the `great-expectations` validator for jsonl as it uses pandas to read in the data). [Link to raised issue](https://github.com/frictionlessdata/frictionless-py/issues/490).\n\n\n### Great Expectations\n\nKnown errors / gotchas:\n- When setting the "default_result_fmt" to "COMPLETE" current default behavour of codebase. You may get errors due to the fact that the returned result from great expectations tries to serialise a `pd.NA` (as a value sample in you row that failed an expectation) when writing the result as a json blob. This can be avoided by setting the "default_result_fmt" to "BASIC" as seen in the Python example above. [Link to raised issue](https://github.com/great-expectations/great_expectations/issues/2029).\n\n\n#### Additional Parameters\n\n- `default_result_fmt`: This is passed to the GE validator, if unset default option is to set the value to `"COMPLETE"`. This value sets out how much information to be returned in the result from each "expectation". For more information [see here](https://docs.greatexpectations.io/en/v0.4.0/result_format.html). Also note the safest option is to set it to `"BASIC"` for reasons discussed in the gotcha section above.\n\n- `ignore_missing_cols`: Will not fail if columns don\'t exist in data but do in metadata (it ignores this).\n\n\n## Process Diagram\n\nHow logic works\n\n![](images/data_linter_process.png)\n\n## How to update\n\nWe have tests that run on the current state of the `poetry.lock` file (i.e. the current dependencies). We also run tests based on the most up to date dependencies allowed in `pyproject.toml`. This allows us to see if there will be any issues when updating dependences. These can be run locally in the `tests` folder.\n\nWhen updating this package, make sure to change the version number in `pyproject.toml` and describe the change in CHANGELOG.md.\n\nIf you have changed any dependencies in `pyproject.toml`, run `poetry update` to update `poetry.lock`.\n\nOnce you have created a release in GitHub, to publish the latest version to PyPI, run:\n\n```bash\npoetry build\npoetry publish -u <username>\n```\n\nHere, you should substitute <username> for your PyPI username. In order to publish to PyPI, you must be an owner of the project.',
    'author': 'Thomas Hirsch',
    'author_email': 'thomas.hirsch@digital.justice.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moj-analytical-services/data_linter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.9',
}


setup(**setup_kwargs)
