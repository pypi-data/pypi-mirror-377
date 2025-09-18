# tap-gainsightpx

`tap-gainsightpx` is a Singer tap for GainsightPX.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.


## Installation

Install from PyPi:

```bash
pipx install tap-gainsightpx
```

Install from GitHub:

```bash
pipx install git+https://github.com/Widen/tap-gainsightpx.git@main
```


## Configuration

### Accepted Config Options


A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-gainsightpx --about
```

<!--
This section can be created by copy-pasting the CLI output from:

```
tap-gainsightpx --about --format=markdown
```
-->

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| api_url             | False    | https://api.aptrinsic.com/v1 | The base url for GainsightPX service. See GainsightPX docs. |
| api_key             | True     | None    | The api key to authenticate against the GainsightPX service |
| page_size           | False    |     500 | The number of records to return from the API in single page.Default and Max is 500. |
| start_date          | False    | 2022-10-26T00:00:00Z | The earliest record date to sync (inclusive '>='). ISO Format |
| end_date            | False    | 2022-10-27T00:00:00Z | The latest record date to sync (inclusive '<='). ISO format. |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization
See the [GainsightPX documentation](https://support.gainsight.com/PX/API_for_Developers/02Usage_of_Different_APIs/Work_with_the_Gainsight_PX_REST_API#Sample_API_Calls) 
for how to create an API key and find your base url.

## Usage

You can easily run `tap-gainsightpx` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-gainsightpx --version
tap-gainsightpx --help
tap-gainsightpx --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_gainsightpx/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-gainsightpx` CLI interface directly using `poetry run`:

```bash
poetry run tap-gainsightpx --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-gainsightpx
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-gainsightpx --version
# OR run a test `elt` pipeline:
meltano elt tap-gainsightpx target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
