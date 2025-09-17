# leap-bundle

Command line tool to create model bundles for Liquid Edge AI Platform ([LEAP](https://leap.liquid.ai)).

This tool enables everyone to create, manage, and download AI model bundles for deployment on edge devices. Upload your model directories, track bundle creation progress, and download optimized bundles ready for mobile integration.

See the [documentation](https://leap.liquid.ai/docs/leap-bundle/quick-start) for more details.

## Installation

```bash
pip install leap-bundle
```

## Commands

| Command | Description |
| --- | --- |
| `leap-bundle login <api-token>` | Authenticate with LEAP using API token |
| `leap-bundle whoami` | Show current authenticated user |
| `leap-bundle logout` | Logout from LEAP |
| `leap-bundle config` | Show current configuration |
| `leap-bundle validate <input-path>` | Validate directory for bundle creation |
| `leap-bundle create` | Submit new bundle request |
| `leap-bundle list` | List all bundle requests |
| `leap-bundle list <request-id>` | Show details of a specific request |
| `leap-bundle cancel <request-id>` | Cancel a bundle request |
| `leap-bundle download <request-id>` | Download the bundle file for a specific request |

## License

[LFM Open License v1.0](https://www.liquid.ai/lfm-license)
