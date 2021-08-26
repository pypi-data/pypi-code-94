# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shellous']

package_data = \
{'': ['*']}

install_requires = \
['immutables>=0.16,<0.17']

setup_kwargs = {
    'name': 'shellous',
    'version': '0.2.0',
    'description': 'shellous: Run Processes and Pipelines',
    'long_description': 'shellous: Run Processes and Pipelines\n=====================================\n\n[![PyPI](https://img.shields.io/pypi/v/shellous)](https://pypi.org/project/shellous/) [![CI](https://github.com/byllyfish/shellous/actions/workflows/ci.yml/badge.svg)](https://github.com/byllyfish/shellous/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/byllyfish/shellous/branch/main/graph/badge.svg?token=W44NZE89AW)](https://codecov.io/gh/byllyfish/shellous)\n\nshellous is an asyncio library that provides a concise API for running subprocesses. It is \nsimilar to and inspired by `sh`.\n\n```python\nimport asyncio\nimport shellous\n\nsh = shellous.context()\n\nasync def main():\n    result = await (sh("ls") | sh("grep", "README"))\n    print(result)\n\nasyncio.run(main())\n```\n\nBenefits\n--------\n\n- Run programs asychronously in a single line.\n- Easily capture output or redirect stdin, stdout and stderr to files.\n- Easily construct pipelines.\n- Runs on Linux, MacOS and Windows.\n\nRequirements\n------------\n\n- Requires Python 3.9 or later.\n- Requires an asyncio event loop.\n\nBasic Usage\n-----------\n\nStart the asyncio REPL by typing `python3 -m asyncio`, and import the **shellous** module:\n\n```python-repl\n>>> import shellous\n```\n\nBefore we can do anything else, we need to create a **context**. Store the context in a \nshort variable name like `sh` because we\'ll be typing it a lot.\n\n```python-repl\n>>> sh = shellous.context()\n```\n\nNow, we\'re ready to run our first command. Here\'s one that runs `echo "hello, world"`.\n\n```python-repl\n>>> await sh("echo", "hello, world")\n\'hello, world\\n\'\n```\n\nThe first argument is the program name. It is followed by zero or more separate arguments.\n\nA command does not run until you `await` it. Here, we create our own echo command with "-n"\nto omit the newline. Note, `echo("abc")` is the same as `echo -n "abc"`.\n\n```python-repl\n>>> echo = sh("echo", "-n")\n>>> await echo("abc")\n\'abc\'\n```\n\n[More on commands...](docs/commands.md)\n\nResults and Exit Codes\n----------------------\n\nWhen you `await` a command, it captures the standard output and returns it. You can optionally have the\ncommand return a `Result` object. The `Result` object will contain more information about the command \nexecution including the `exit_code`. To return a result object, set `return_result` option to `True`.\n\n```python-repl\n>>> await echo("abc").set(return_result=True)\nResult(output_bytes=b\'abc\', exit_code=0, cancelled=False, encoding=\'utf-8\', extra=None)\n```\n\nThe above command had an exit_code of 0.\n\nIf a command exits with a non-zero exit code, it raises a `ResultError` exception that contains\nthe `Result` object.\n\n```python-repl\n>>> await sh("cat", "does_not_exist")\nTraceback (most recent call last):\n  ...\nshellous.result.ResultError: Result(output_bytes=b\'\', exit_code=1, cancelled=False, encoding=\'utf-8\', extra=None)\n```\n\n[More on results...](docs/results.md)\n\nRedirecting Standard Input\n--------------------------\n\nYou can change the standard input of a command by using the `|` operator.\n\n```python-repl\n>>> cmd = "abc" | sh("wc", "-c")\n>>> await cmd\n\'       3\\n\'\n```\n\nTo redirect stdin using a file\'s contents, use a `Path` object from `pathlib`.\n\n```python-repl\n>>> from pathlib import Path\n>>> cmd = Path("README.md") | sh("wc", "-l")\n>>> await cmd\n\'     210\\n\'\n```\n\n[More on redirection...](docs/redirection.md)\n\nRedirecting Standard Output\n---------------------------\n\nTo redirect standard output, use the `|` operator.\n\n```python-repl\n>>> output_file = Path("/tmp/output_file")\n>>> cmd = sh("echo", "abc") | output_file\n>>> await cmd\n\'\'\n>>> output_file.read_bytes()\nb\'abc\\n\'\n```\n\nTo redirect standard output with append, use the `>>` operator.\n\n```python-repl\n>>> cmd = sh("echo", "def") >> output_file\n>>> await cmd\n\'\'\n>>> output_file.read_bytes()\nb\'abc\\ndef\\n\'\n```\n\n[More on redirection...](docs/redirection.md)\n\nRedirecting Standard Error\n--------------------------\n\nBy default, standard error is not captured. To redirect standard error, use the `stderr`\nmethod.\n\n```python-repl\n>>> cmd = sh("cat", "does_not_exist").stderr(shellous.STDOUT)\n>>> await cmd.set(exit_codes={0,1})\n\'cat: does_not_exist: No such file or directory\\n\'\n```\n\nYou can redirect standard error to a file or path. \n\nTo redirect standard error to the hosting program\'s `sys.stderr`, use the INHERIT redirect\noption.\n\n```python-repl\n>>> cmd = sh("cat", "does_not_exist").stderr(shellous.INHERIT)\n>>> await cmd\ncat: does_not_exist: No such file or directory\nTraceback (most recent call last):\n  ...\nshellous.result.ResultError: Result(output_bytes=b\'\', exit_code=1, cancelled=False, encoding=\'utf-8\', extra=None)\n```\n\n[More on redirection...](docs/redirection.md)\n\nPipelines\n---------\n\nYou can create a pipeline by combining commands using the `|` operator.\n\n```python-repl\n>>> pipe = sh("ls") | sh("grep", "README")\n>>> await pipe\n\'README.md\\n\'\n```\n\nIteration\n---------\n\nYou can loop over a command\'s output.\n\n```python-repl\n>>> async for line in pipe:\n...   print(line.rstrip())\n... \nREADME.md\n```\n\nAsync With\n----------\n\nYou can use `async with` to interact with the process streams directly. You have to be careful; you\nare responsible for correctly reading and writing multiple streams at the same time.\n\n```python-repl\n>>> runner = pipe.runner()\n>>> async with runner as (stdin, stdout, stderr):\n...   data = await stdout.readline()\n...   print(data)\n... \nb\'README.md\\n\'\n```\n',
    'author': 'Bill Fisher',
    'author_email': 'william.w.fisher@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/byllyfish/shellous',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
