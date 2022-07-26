# bc-lifehash-python - The python implementation

* <img src="images/logos/crypto-commons-super-simple.png" width=16 valign="bottom">&nbsp;&nbsp; ***part of the [crypto commons](https://github.com/BlockchainCommons/crypto-commons/blob/master/README.md) technology family***

### _by [Bryan Bishop](https://github.com/kanzure) & [Cramium Solutions](https://cramiumsolutions.com/)_

LifeHash is a method of hash visualization. This is a python implementation of [bc-lifehash](https://github.com/BlockchainCommons/bc-lifehash), see there for an overview of LifeHash.

## Notes on This Implementation

This python library should probably be replaced with bindings to the C implementation, which is the "canonical" reference implementation.

## Implementations

| Type | Name | Language | Note |
|------|------|----------|------|
| Reference | [bc-lifehash](https://github.com/BlockchainCommons/bc-lifehash) | C++/C
| Third-Party | [bc-lifehash-python](https://github.com/BlockchainCommons/bc-lifehash-python) | Python | [Cramium](https://cramiumsolutions.com/)
| Reference | [LifeHash](https://github.com/BlockchainCommons/LifeHash) | Swift
| Reference | [LifeHash](https://github.com/BlockchainCommons/LifeHash) | Mathematica/Wolfram Language | `version1` only

## Command-Line Tools

[bc-lifehash-cli](https://github.com/BlockchainCommons/bc-lifehash-cli) is a command line tool written in C++ that generates LifeHash images as PNG files.


## Installation Instructions

```bash
$ pip3 install lifehash
```

## Usage Instructions

```python
from lifehash.lifehash import LifeHash, LifeHashVersion
image = LifeHash.make_from(b"hello world", version=LifeHashVersion.version2, module_size=1, has_alpha=True)
```

### Testing

```bash
$ python3 -m unittest lifehash/lifehash.py
```

### Building

```bash
$ python3 -m build
```

For releases: `git tag` and push, then `twine upload dist/*`

### Version History

#### 1.00 (July 5, 2022)

First version of `bc-lifehash-python` contributed to Blockchain COmmons.

## Origin, Authors, Copyright & Licenses

LifeHash is released under the BSD-2-Clause license from [Cramium Solutions](https://cramiumsolutions.com). See [LICENSE.md](LICENSE.md) for more info.

## Dependencies

This LifeHash library is self-contained and has no dependencies.

## Financial Support

LifeHash is also a project of [Blockchain Commons](https://www.blockchaincommons.com/). We are proudly a "not-for-profit" social benefit corporation committed to open source & open development. Our work is funded entirely by donations and collaborative partnerships with people like you. Every contribution will be spent on building open tools, technologies, and techniques that sustain and advance blockchain and internet security infrastructure and promote an open web.

To financially support further development of LifeHash and other projects, please consider becoming a Patron of Blockchain Commons through ongoing monthly patronage as a [GitHub Sponsor](https://github.com/sponsors/BlockchainCommons). You can also support Blockchain Commons with bitcoins at our [BTCPay Server](https://btcpay.blockchaincommons.com/).

### Project Sponsors

The python implementation of LifeHash is built and sponsored by [Cramium Solutions](https://cramiumsolutions.com/).

## Contributing

We encourage public contributions through issues and pull-requests! Please review [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our development process. All contributions to this repository require a GPG signed [Contributor License Agreement](./CLA.md).

### Discussions

The best place to talk about Blockchain Commons and its projects is in our GitHub Discussions areas.

[**Wallet Standard Discussions**](https://github.com/BlockchainCommons/AirgappedSigning/discussions). For standards and open-source developers who want to talk about wallet standards, please use the Discussions area of the [Airgapped Signing repo](https://github.com/BlockchainCommons/AirgappedSigning). This is where you can talk about projects like our [LetheKit](https://github.com/BlockchainCommons/bc-lethekit) and command line tools such as [seedtool](https://github.com/BlockchainCommons/bc-seedtool-cli), both of which are intended to testbed wallet technologies, plus the libraries that we've built to support your own deployment of wallet technology such as [bc-bip39](https://github.com/BlockchainCommons/bc-bip39), [bc-slip39](https://github.com/BlockchainCommons/bc-slip39), [bc-shamir](https://github.com/BlockchainCommons/bc-shamir), [Sharded Secret Key Reconstruction](https://github.com/BlockchainCommons/bc-sskr), [bc-ur](https://github.com/BlockchainCommons/bc-ur), and the [bc-crypto-base](https://github.com/BlockchainCommons/bc-crypto-base). If it's a wallet-focused technology or a more general discussion of wallet standards,discuss it here.

[**Blockchain Commons Discussions**](https://github.com/BlockchainCommons/Community/discussions). For developers, interns, and patrons of Blockchain Commons, please use the discussions area of the [Community repo](https://github.com/BlockchainCommons/Community) to talk about general Blockchain Commons issues, the intern program, or topics other than the [Gordian System](https://github.com/BlockchainCommons/Gordian/discussions) or the [wallet standards](https://github.com/BlockchainCommons/AirgappedSigning/discussions), each of which have their own discussion areas.

### Other Questions & Problems

As an open-source, open-development community, Blockchain Commons does not have the resources to provide direct support of our projects. Please consider the discussions area as a locale where you might get answers to questions. Alternatively, please use this repository's [issues](./issues) feature. Unfortunately, we can not make any promises on response time.

If your company requires support to use our projects, please feel free to contact us directly about options. We may be able to offer you a contract for support from one of our contributors, or we might be able to point you to another entity who can offer the contractual support that you need.

### Credits

The following people directly contributed to this repository. You can add your name here by getting involved — the first step is to learn how to contribute from our [CONTRIBUTING.md](./CONTRIBUTING.md) documentation.

| Name | Role | Github | Email | GPG Fingerprint |
|---|---|---|---|---|
| Bryan Bishop | Developer | [@kanzure](https://github.com/kanzure) | \<kanzure@gmail.com\> | 0E4C A12B E16B E691 56F5 40C9 984F 10CC 7716 9FD2 |

## Responsible Disclosure

We want to keep all our software safe for everyone. If you have discovered a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner. We are unfortunately not able to offer bug bounties at this time.

We do ask that you offer us good faith and use best efforts not to leak information or harm any user, their data, or our developer community. Please give us a reasonable amount of time to fix the issue before you publish it. Do not defraud our users or us in the process of discovery. We promise not to bring legal action against researchers who point out a problem provided they do their best to follow the these guidelines.

## Reporting a Vulnerability

Please report suspected security vulnerabilities in private via email to ChristopherA@BlockchainCommons.com (do not use this email for support). Please do NOT create publicly viewable issues for suspected security vulnerabilities.

The following keys may be used to communicate sensitive information to developers:

| Name              | Fingerprint                                        |
| ----------------- | -------------------------------------------------- |
| Christopher Allen | FDFE 14A5 4ECB 30FC 5D22  74EF F8D3 6C91 3574 05ED |

You can import a key by running the following command with that individual’s fingerprint: `gpg --recv-keys "<fingerprint>"` Ensure that you put quotes around fingerprints that contain spaces.
