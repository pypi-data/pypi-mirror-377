# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.5] - 16/09/2025

### Added

- docs revamping, and improved user story in examples

## [0.6.4] - 16/09/2025

### Changed

- release to public repo in github instead of gitlab
- fix breathe model json naming scheme

## [0.6.3] - 16/09/2025

### Changed

- Updated `download_designs` function to use naming convention for Simulink compatibility, and added info to the description metadata

## [0.6.2] - 15/09/2025

### Added

- pypi upload steps

## [0.6.1] - 15/09/2025

### Added

- release of examples to public repo

## [0.6.0] - 12/09/2025

### Added

- Results handler class

## [0.5.10] - 11/09/2025

### Added

- Cycler and Parameter bounds validation and handling

## [0.5.9] - 11/09/2025

### Fixed

- Typo in `get_batteries` doc string

## [0.5.8] - 11/09/2025

### Fixed

- case where API calls will fail with incorrect permissions (403) immediately after first sign-up

## [0.5.7]

### Changed

- increased login timeout from `20s` to `60s`
- changed `get_batteries` to show just the names and not the IDs

## [0.5.6]

### Fixed

- formatted docs and default conditions

## [0.5.5]

### Added

- ability to use run_sim with format changes and also download designs

### Fixed

- changed plastic to pouch for allowable format material

## [0.5.4]

### Updated

- Updated mkdocs config to allow integration with doc-site

## [0.5.3]

### Fixed

- Change v[0] to be last point of rest for DCIR

## [0.5.2] - 27/08/2025

### Fixed

- Bug in DCIR calc

## [0.5.1] - 26/08/2025

### Changed

- Names of initialSocs -> initialSoC and initialTemperature_Ks -> initialTemperature_degC when calling api to run a sim

## [0.5.0] - 21/08/2025

### Added

- `logout()` method on the authorisation object.

### Changed

- api methods will now raise exceptions in case of error, instead of returning `None`

### Fixed

- case where some design names could end up overwriting each-other

## [0.4.3] - 25/06/2025

### Changed

- update docs
- rename plot_dynamic_kpis

## [0.4.2] - 28/07/2025

### Added

- get_updated_format api function to retrieve and update a battery format

### Changed

- Updated Readme to include a form factor change example

### Fixed

- recommend `venv\Scripts\activate` in README since it works on CMD and powershell

## [0.4.1] - 21/07/2025

### Changed

- Add a number suffix to the downloaded json file

## [0.4.0] - 18/07/2025

### Added

- `download_design` method to download the encrypted battery design

## [0.3.0] - 02/07/2025

### Added

- `get_service_version` method to get the API version
- locking around device auth to make it threadsafe

## [0.2.6] - 25/06/2025

### Changed

- cell list now comes from the backend api rather than the model

## [0.2.5] - 25/06/2025

### Added

- Version number to latest docs
- Change battery format

### Fixed

- nans in KPI sensitivity for volume

## [0.2.4] - 17/06/2025

### Added

- Docs

## [0.2.3] - 12/06/2025

### Added

- Update config to prod server

## [0.2.2] - 11/06/2025

### Added

- Update notebooks

## [0.2.1] - 09/06/2025

### Fixed

- Handle case where token is already expired so the endpoints return 401

## [0.1.0] - 05/06/2025

### Added

- Token storage to persist logins accross python sessions
- Refresh token usage to refresh access token when needed
