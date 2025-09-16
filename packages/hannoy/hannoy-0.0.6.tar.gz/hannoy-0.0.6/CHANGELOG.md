# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.6](https://github.com/nnethercott/hannoy/compare/v0.0.5...v0.0.6) - 2025-09-15

### Added

- *(py)* improve type stubs for lsp support ([#85](https://github.com/nnethercott/hannoy/pull/85))
- Add minimal Python bindings with pyo3  ([#83](https://github.com/nnethercott/hannoy/pull/83))
- *(hnsw)* Add alpha to build parameters ([#84](https://github.com/nnethercott/hannoy/pull/84))
- make pre-fetching opt-in ([#79](https://github.com/nnethercott/hannoy/pull/79))
- Improve cold-start search latencies with madvise  ([#72](https://github.com/nnethercott/hannoy/pull/72))

### Fixed

- *(hnsw)* make error into debug trace ([#86](https://github.com/nnethercott/hannoy/pull/86))
- *(reader)* truncate quantized ItemIter vectors to original len ([#80](https://github.com/nnethercott/hannoy/pull/80))

### Other

- fix conversion for binary vectors ([#88](https://github.com/nnethercott/hannoy/pull/88))
- update README.md ([#87](https://github.com/nnethercott/hannoy/pull/87))
- Add method to vector codec trait for quantization info ([#82](https://github.com/nnethercott/hannoy/pull/82))
- new logo courtesy of flux.1-dev ([#75](https://github.com/nnethercott/hannoy/pull/75))
- Arroy feature flag ([#73](https://github.com/nnethercott/hannoy/pull/73))

## [0.0.5](https://github.com/nnethercott/hannoy/compare/v0.0.4...v0.0.5) - 2025-08-25

### Added

- parallelize vanama link patching ([#71](https://github.com/nnethercott/hannoy/pull/71))

### Other

- clean up the rust docs  ([#67](https://github.com/nnethercott/hannoy/pull/67))
- loosely define the steppe version ([#69](https://github.com/nnethercott/hannoy/pull/69))
- Use a linear algorithm on small number of candidates
- add codspeed badge to readme
- *(perf)* migrate to divan ([#64](https://github.com/nnethercott/hannoy/pull/64))
- add criterion benchmarks ([#59](https://github.com/nnethercott/hannoy/pull/59))
- Update README.md
- update readme ([#58](https://github.com/nnethercott/hannoy/pull/58))
- move config and add new settings ([#55](https://github.com/nnethercott/hannoy/pull/55))
- bump minor version in snapshots ([#56](https://github.com/nnethercott/hannoy/pull/56))

## [0.0.4](https://github.com/nnethercott/hannoy/compare/v0.0.3...v0.0.4) - 2025-08-14

### Other

- remove duplicate test
- Speedup search when candidates are disjoint with the index
- Add comment
- skip items that were deleted
- Simplify and rename the test
- real minimal repro
- Add a test to reproduce #52
- release-plz ([#50](https://github.com/nnethercott/hannoy/pull/50))
