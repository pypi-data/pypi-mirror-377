Security Policy
===============

Reporting a Vulnerability
-------------------------

Please email security reports privately to security@example.com. Include:
- A clear description and proof-of-concept if possible
- Impact assessment and affected versions
- Preferred credit name

We will acknowledge within 3 business days and provide a remediation plan and target timeline.

Embargo and Disclosure
----------------------
- Default embargo window: 90 days from initial report, extendable by mutual agreement.
- Coordinated disclosure: We will publish a GitHub Security Advisory and release patched versions before public disclosure.
- CVE: We will request a CVE ID via GitHub Advisories and reference it in the release notes and changelog.

Supported Versions
------------------
- We patch the latest minor release and the previous minor when feasible.

Signing and Integrity
---------------------
- Git tags and PyPI artifacts are signed with our GPG release key.
- Checksums (SHA256SUMS) and a CycloneDX SBOM are attached to GitHub Releases.

Supply Chain
------------
- CI runs on Linux, macOS, and Windows, with tests and fuzz/property checks.
- pip-audit scans Python dependencies during CI.

Contact
-------
- security@example.com

## Security Policy

Report vulnerabilities privately to maintainers. Avoid filing public issues for undisclosed vulnerabilities.

We aim to patch critical issues quickly and issue a security release with notes.


