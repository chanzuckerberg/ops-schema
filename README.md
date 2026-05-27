# OPS Data Standard

This repository contains the data standard specification for Optical Pooled Screening (OPS) experiments.

## Overview

The OPS Data Standard defines the structure, format, and requirements for organizing and sharing data from Optical Pooled Screening experiments. This standard enables:

- Consistent data organization across labs and institutions
- Interoperability between analysis tools
- Data sharing and reproducibility
- Integration with the CELLxGENE ecosystem

### Data Model

OPS submissions are organized in a three-level hierarchy:

- **Collection** — one per submission; groups pseudobulk aggregations from a single publication.
- **Pseudobulk Aggregation** — the lab-defined dataset that the perturbation library, single-cell features, and image store hang off of. Not necessarily one physical screen run: a lab may pool cells from multiple runs into a single aggregation.
- **Visualization (Embedding)** — one or more per aggregation. Each visualization renders the aggregation through one or more embeddings (UMAP, PHATE, t-SNE, …) carried in a single `aggregated_data.h5ad`.

See the [schema specification](standards/ops/0.1.0/schema.md) for the full data model and field-level requirements.

## Documentation

The schema specification is available in the `standards/` directory:

- [OPS Schema v0.1.0](standards/ops/0.1.0/schema.md)

## Project Status

This project is under active development. The schema is currently in draft status (v0.1.0) with pending items that need to be resolved before the v1.0.0 release. If you are interested in contributing, check out ["help wanted"](https://github.com/chanzuckerberg/ops-schema/issues?q=label%3A"help+wanted"+is%3Aissue+is%3Aopen) issues.

## Getting Started

To use this schema for your OPS data:

1. Review the [schema specification](standards/ops/0.1.0/schema.md)
2. Organize your data according to the specified directory structure
3. Validate your data against the schema requirements using the [validator](validator/)
4. Open an issue or reach out if you have questions about submitting data

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to submit issues and feature requests
- How to propose changes to the schema
- Code of conduct expectations

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to opensource@chanzuckerberg.com.

## Reporting Security Issues

Please note: If you believe you have found a security issue, please responsibly disclose by contacting us at security@chanzuckerberg.com. See [SECURITY.md](SECURITY.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

For questions or support, open an issue in this repository.

## Acknowledgments

This schema was developed in collaboration with the Chan Zuckerberg Initiative Science team and the broader OPS research community.

The OPS Data Standard builds on [OME-Zarr](https://ngff.openmicroscopy.org/) and draws on the [`ome-zarr-py`](https://github.com/ome/ome-zarr-py) reference implementation, which is distributed under the BSD 2-Clause License. We are grateful to the OME community for their work establishing open standards for bioimaging data.
