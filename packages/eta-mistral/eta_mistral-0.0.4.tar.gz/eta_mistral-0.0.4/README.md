# ETA MISTRAL

This repository represents the software implementation of the MISTRAL method. It provides a CLI to configure the optimization in the backend and a web interface for plotting. Here also the graph representation of th modelled system is visible.

## Usage

Following the cli this approach is applied: ![flow diagram](./docs/images/flow_chart_mistral_method.png)

## Development

For the development an overview of the modules is provided: ![module overview](./docs/images/modul_overview_mistral.png)


### Installation
To install the project along with its development dependencies, execute the following command:

    poetry install

Followed by

    poetry run pre-commit install

After this you are ready to perform the first commits to the repository.

Pre-commit ensures that the repository accepts your commit, automatically fixes some code styling problems and provides some hints for better coding.

### Adding dependencies

Adding dependencies to the project can be done via

    poetry add <package-name>@latest

## Important Note for the CLI Application

Do not forget to close (ctrl + C) the dash server when exiting the application.
