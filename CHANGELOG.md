<!--
Do *NOT* add changelog entries here!

This changelog is managed by towncrier and is compiled at release time.

See https://github.com/python-attrs/attrs/blob/main/.github/CONTRIBUTING.md#changelog for details.
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Calendar Versioning](https://calver.org/). The **first number** of the version is the year. The **second number** is incremented with each release, starting at 1 for each year. The **third number** is for emergencies when we need to start branches for older releases, or for very minor changes.

<!-- towncrier release notes start -->

## [2024.1.2](https://github.com/softboiler/boilercv/tree/2024.1.2)

### Changes

- Sign commits and tags for releases ([471ce81](https://github.com/softboiler/boilercv/commit/471ce81841bc318e5d7780181355dc0dda8ad658))
- Resolve two incompatible `numpy` pins in Binder requirements ([#224](https://github.com/softboiler/boilercv/issues/224))

## [2024.1.1](https://github.com/softboiler/boilercv/tree/2024.1.1)

### Changes

- `boilercv_pipeline`: Compare tracking approaches
- Structure equations for testability. Add dimensionless parameters to `boilercv`. ([#182](https://github.com/softboiler/boilercv/issues/182))
- `boilercv_pipeline`: Generalize equation generator for separate equation sources ([#185](https://github.com/softboiler/boilercv/issues/185))
- Stabilize `boilercv.morphs.ContextMorph`. Implement subcooling correlations ([#188](https://github.com/softboiler/boilercv/issues/188))
- Generate arbitrary solutions to correlations ([#189](https://github.com/softboiler/boilercv/issues/189))
- Migrate stabilized `Morph` functionality to `boilercv` ([#194](https://github.com/softboiler/boilercv/issues/194))
- Decompress datasets on first access
- Refactor out model functionality pertaining to model synchronization
- Separate project paths from data paths
- `boilercv_pipeline`: Implement bubble lifetime tracking
- Support building of documentation notebooks with example data (migrated to `boilercore`)
- Fix broken links due to organization question in template ([#205](https://github.com/softboiler/boilercv/issues/205))
- Publish first version under CalVer ([#212](https://github.com/softboiler/boilercv/issues/212))
- Investigate upstream issue with `netcdf4==1.7.1` on Linux. Pin `netcdf4` for now ([#215](https://github.com/softboiler/boilercv/issues/215))
- `boilercv`: Add `xarray` back to main requirements now that Pandas 2.0 is supported
- Specify `pandas` and `xarray` extras and remove manual pins now that extras support Python 3.11
- `boilercv_docs`: Set up documentation to facilitate theory development
- `boilercv_pipeline`: Implement bubble statistics
- `boilercv_pipeline`: Support asynchronous granular pipeline runs
- Minimize monkeypatching in tests. Decouple most paths
- `boilercv_pipeline`: Export contours and centers
- Separate concerns of caching, hashing, and finding the minimal necessary namespace (migrated to `boilercore`)
- `boilercv_pipeline`:Publish example data and implement pipeline testing
- `boilercv_pipeline`: Compare center-finding approaches
- `boilercv_pipeline`: Get object sizes assuming objects are approximately circular
- `boilercv_tests`: Allow saving plots from notebook tests
- `boilercv_docs`: Allow live code experimentation in docs using Binder
- Test on MacOSX, Ubuntu, and Windows, supporting Python 3.11 and 3.12
- Specify ground-up container build with `.devcontainer` for Codespaces and local testing
- Automatically synchronize the contributor environment (migrated to `copier-python`)
- Separate packaged code, tests, documentation, and pipeline
- Implement generic `Morph` and `ContextMorph`, Pydantic-powered mapping transforms
- Implement conversion from PNG to LaTeX
- Implement conversion from LaTeX to SymPy equations
- Implement and cite subcooled bubble collapse correlations sourced from paper PDFs
- Equation generation framework
- Formalize release workflow with attestations

## [0.0.6](https://github.com/softboiler/boilercv/releases/tag/0.0.6)

- Dummy release, figuring out PyPI publishing with OIDC and artifact attestations

## [0.0.5](https://github.com/softboiler/boilercv/releases/tag/0.0.5)

- Dummy release, see above

## [0.0.4](https://github.com/softboiler/boilercv/releases/tag/0.0.4)

- Dummy release, see above

## [0.0.3](https://github.com/softboiler/boilercv/releases/tag/0.0.3)

- Dummy release, see above

## [0.0.2](https://github.com/softboiler/boilercv/releases/tag/0.0.2)

- Dummy release, see above

## [0.0.1](https://github.com/softboiler/boilercv/releases/tag/0.0.1)

- Freeze requirements used for pipeline reproduction in `repro.txt` for this release
- Remove `check_cv` stage
- Make stages aware of unprocessed datasets
- Document contour finding

## [0.0.0](https://github.com/softboiler/boilercv/releases/tag/0.0.0)

- Freeze requirements used for pipeline reproduction in `repro.txt` for this release
