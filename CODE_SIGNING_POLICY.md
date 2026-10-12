# FOU — Code Signing Policy

**Project:** FOU — Crypto Portfolio Tracker  
**Repository:** https://github.com/FOU-SHREX/FOU  
**Maintainer:** [FOU-SHREX](https://github.com/FOU-SHREX)

## Status

FOU v2.5.0 has been publicly released on GitHub. The current Windows executable is unsigned, and the project is applying to SignPath Foundation for free open-source code signing.

No FOU release will be described as SignPath-signed until the project is approved and the executable's signature is verified.

For approved future releases, the required acknowledgement will be:

> Free code signing provided by SignPath.io, certificate by SignPath Foundation.

## Source and trusted builds

- The canonical public source is maintained at [FOU-SHREX/FOU](https://github.com/FOU-SHREX/FOU).
- Official release candidates are built from the public repository using [GitHub Actions](https://github.com/FOU-SHREX/FOU/actions) on GitHub-hosted runners.
- Windows, Linux, and macOS build artifacts are produced separately. Successful compilation and packaging do not replace platform-specific runtime testing.
- If SignPath approves the project, Windows release signing will be integrated with its trusted-build and origin-verification process. Only eligible artifacts originating from the approved public workflow will be submitted for signing.
- Release candidates are reviewed before publication. Signed releases will require the SignPath approval process configured for the project.
- No signing credentials, API tokens, or private keys will be stored in the source repository.

## Team roles

FOU is currently maintained by one person under the GitHub account **FOU-SHREX**:

- **Author / committer:** FOU-SHREX — maintains source code and build configuration.
- **Reviewer:** FOU-SHREX — reviews changes before release; outside contributions must be reviewed before merging.
- **Release signing approver:** FOU-SHREX — responsible for manually approving releases if a SignPath signing policy becomes available.

These roles will be updated if more maintainers join. Multi-factor authentication will be required for accounts that access code signing and the source repository.

## Privacy and security

FOU is a cryptocurrency watchlist, not a wallet or trading platform. The client stores a list of coin symbols and identifiers locally. For market data, the app contacts a hosted FOU backend; the backend queries third-party market-data services. The GUI can also download coin logos from remote image URLs. The Help button opens the project's GitHub README in the user's browser.

The project publishes its privacy policy at [PRIVACY.md](PRIVACY.md). It describes local storage, backend requests, network interactions, and relevant third-party services.

## Release and installation

- Release downloads will identify the source revision and version they were built from.
- Installers, once available, will provide a normal Windows uninstall path. Portable builds can be removed by deleting the application folder; user data is stored separately and can be removed manually.
- Any unsigned release will be clearly labeled **unsigned** and will not be represented as publisher-verified.
- The first public desktop GUI release is [v2.5.0](https://github.com/FOU-SHREX/FOU/releases/tag/v2.5.0).

**This policy documents the intended signing procedure. It does not grant any software a trusted publisher status or prove that current binaries are signed.**
