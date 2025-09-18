# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tap_gainsightpx', 'tap_gainsightpx.tests']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.25.1,<3.0.0', 'singer-sdk>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['tap-gainsightpx = '
                     'tap_gainsightpx.tap:TapGainsightPX.cli']}

setup_kwargs = {
    'name': 'tap-gainsightpx',
    'version': '1.0.8',
    'description': '`tap-gainsightpx` is a Singer tap for GainsightPX, built with the Meltano Singer SDK.',
    'long_description': "# tap-gainsightpx\n\n`tap-gainsightpx` is a Singer tap for GainsightPX.\n\nBuilt with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.\n\n\n## Installation\n\nInstall from PyPi:\n\n```bash\npipx install tap-gainsightpx\n```\n\nInstall from GitHub:\n\n```bash\npipx install git+https://github.com/Widen/tap-gainsightpx.git@main\n```\n\n\n## Configuration\n\n### Accepted Config Options\n\n\nA full list of supported settings and capabilities for this\ntap is available by running:\n\n```bash\ntap-gainsightpx --about\n```\n\n<!--\nThis section can be created by copy-pasting the CLI output from:\n\n```\ntap-gainsightpx --about --format=markdown\n```\n-->\n\n| Setting             | Required | Default | Description |\n|:--------------------|:--------:|:-------:|:------------|\n| api_url             | False    | https://api.aptrinsic.com/v1 | The base url for GainsightPX service. See GainsightPX docs. |\n| api_key             | True     | None    | The api key to authenticate against the GainsightPX service |\n| page_size           | False    |     500 | The number of records to return from the API in single page.Default and Max is 500. |\n| start_date          | False    | 2022-10-26T00:00:00Z | The earliest record date to sync (inclusive '>='). ISO Format |\n| end_date            | False    | 2022-10-27T00:00:00Z | The latest record date to sync (inclusive '<='). ISO format. |\n| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |\n| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |\n| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |\n| flattening_max_depth| False    | None    | The max depth to flatten schemas. |\n\n### Configure using environment variables\n\nThis Singer tap will automatically import any environment variables within the working directory's\n`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching\nenvironment variable is set either in the terminal context or in the `.env` file.\n\n### Source Authentication and Authorization\nSee the [GainsightPX documentation](https://support.gainsight.com/PX/API_for_Developers/02Usage_of_Different_APIs/Work_with_the_Gainsight_PX_REST_API#Sample_API_Calls) \nfor how to create an API key and find your base url.\n\n## Usage\n\nYou can easily run `tap-gainsightpx` by itself or in a pipeline using [Meltano](https://meltano.com/).\n\n### Executing the Tap Directly\n\n```bash\ntap-gainsightpx --version\ntap-gainsightpx --help\ntap-gainsightpx --config CONFIG --discover > ./catalog.json\n```\n\n## Developer Resources\n\nFollow these instructions to contribute to this project.\n\n### Initialize your Development Environment\n\n```bash\npipx install poetry\npoetry install\n```\n\n### Create and Run Tests\n\nCreate tests within the `tap_gainsightpx/tests` subfolder and\n  then run:\n\n```bash\npoetry run pytest\n```\n\nYou can also test the `tap-gainsightpx` CLI interface directly using `poetry run`:\n\n```bash\npoetry run tap-gainsightpx --help\n```\n\n### Testing with [Meltano](https://www.meltano.com)\n\n_**Note:** This tap will work in any Singer environment and does not require Meltano.\nExamples here are for convenience and to streamline end-to-end orchestration scenarios._\n\nNext, install Meltano (if you haven't already) and any needed plugins:\n\n```bash\n# Install meltano\npipx install meltano\n# Initialize meltano within this directory\ncd tap-gainsightpx\nmeltano install\n```\n\nNow you can test and orchestrate using Meltano:\n\n```bash\n# Test invocation:\nmeltano invoke tap-gainsightpx --version\n# OR run a test `elt` pipeline:\nmeltano elt tap-gainsightpx target-jsonl\n```\n\n### SDK Dev Guide\n\nSee the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to\ndevelop your own taps and targets.\n",
    'author': 'Josh Lloyd',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Widen/tap-gainsightpx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
