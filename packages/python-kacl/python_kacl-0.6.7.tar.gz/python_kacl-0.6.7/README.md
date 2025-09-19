# python-kacl

[![Build Status](https://gitlab.com/schmieder.matthias/python-kacl/badges/main/pipeline.svg?ignore_skipped=true)](https://gitlab.com/schmieder.matthias/python-kacl)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=schmieder.matthias_python-kacl&metric=coverage)](https://sonarcloud.io/summary/new_code?id=schmieder.matthias_python-kacl)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=schmieder.matthias_python-kacl&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=schmieder.matthias_python-kacl)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=schmieder.matthias_python-kacl&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=schmieder.matthias_python-kacl)

A tool for verifying and modifying changelog in the [**K**eep-**A-C**hange-**L**og](https://keepachangelog.com/en/1.0.0/) format.

- [python-kacl](#python-kacl)
  - [Installation](#installation)
    - [From Source](#from-source)
    - [Pip Package](#pip-package)
    - [Docker](#docker)
    - [pre-commit](#pre-commit)
  - [CLI](#cli)
  - [Initialize a new project](#initialize-a-new-project)
  - [Create a Changelog](#create-a-changelog)
  - [Verify a Changelog](#verify-a-changelog)
  - [Print the current release version](#print-the-current-release-version)
  - [Print a single release changelog](#print-a-single-release-changelog)
  - [Add an entry to an unreleased section](#add-an-entry-to-an-unreleased-section)
  - [Prepare a Changelog for a Release](#prepare-a-changelog-for-a-release)
  - [Changelog Fragments](#changelog-fragments)
    - [Configuration](#configuration)
    - [How It Works](#how-it-works)
    - [Usage Patterns](#usage-patterns)
      - [Automatic Fragment Creation](#automatic-fragment-creation)
      - [Manual Fragment Control](#manual-fragment-control)
    - [Fragment Structure](#fragment-structure)
    - [Release Integration](#release-integration)
    - [Workflow Integration](#workflow-integration)
    - [Benefits](#benefits)
  - [Link Generation](#link-generation)
  - [Squashing releases](#squashing-releases)
    - [Example](#example)
  - [Issue Management Integration](#issue-management-integration)
    - [Adding Comments to Issues](#adding-comments-to-issues)
    - [Command Options](#command-options)
    - [Templating the Comment](#templating-the-comment)
  - [Extensions](#extensions)
    - [Post-release/Hotfix](#post-releasehotfix)
  - [Config file](#config-file)
    - [Default Config](#default-config)
    - [Configuration Parameters](#configuration-parameters)
    - [Template Variables](#template-variables)
  - [Development](#development)

## Installation

`python-kacl` and it `kacl-cli` can be installed either

- from source
- via the pip package `python-kacl`
- docker

All approaches are described in detail within this section.

### From Source

```bash
git clone https://gitlab.com/schmieder.matthias/python-kacl
cd python-kacl
```

**Global Install**

```bash
pip3 install .
```

**Developer Mode**

```bash
pip3 install -e .
```

### Pip Package

The package can simply be retrieves using

```bash
pip3 install python-kacl
```

### Docker

```bash
docker pull mschmieder/kacl-cli:latest
```

The `kacl-cli` is defined as entrypoint. Therefore the image can be used like this

```bash
docker -v $(pwd):$(pwd) -w $(pwd) mschmieder/kacl-cli:latest verify
```

### pre-commit

The package can also be used as a pre-commit hook. Just add the following to your `.pre-commit-config.yaml`

```yaml
- repo: https://gitlab.com/schmieder.matthias/python-kacl
  rev: 'v0.3.0'
  hooks:
    - id: kacl-verify
```

## CLI

```
Usage: kacl-cli [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config PATH  Path to kacl config file  [default: .kacl.conf]
  -f, --file PATH    Path to changelog file  [default: CHANGELOG.md]
  --help             Show this message and exit.

Commands:
  add      Adds a given message to a specified unreleased section.
  get      Returns a given version from the Changelog
  new      Creates a new changelog.
  release  Creates a release for the latest 'unreleased' changes.
  verify   Verifies if the changelog is in "keep-a-changelog" format.
```

## Initialize a new project

```bash
Usage: kacl-cli init [OPTIONS]

  Initializes a project with all necessary kacl setting.

Options:
  -f, --force  Will overwrite existing files.
  --help       Show this message and exit.
```

The `init` command provides a quick way to set up a new project with all necessary KACL files and configuration. This command creates two essential files:

1. **CHANGELOG.md** - A new changelog file with the standard Keep a Changelog format
2. **.kacl.yml** - A complete configuration file with all available options and sensible defaults

**Usage**

```bash
kacl-cli init
```

This will create both files in the current directory. If either file already exists, the command will fail unless you use the `--force` option:

```bash
kacl-cli init --force
```

**Created Files**

The `init` command creates a standard CHANGELOG.md file and copies the complete default configuration. The `.kacl.yml` file includes all available configuration options:

```yaml
kacl:
  file: CHANGELOG.md
  allowed_header_titles:
    - Changelog
    - Change Log
  allowed_version_sections:
    - Added
    - Changed
    - Deprecated
    - Removed
    - Fixed
    - Security
  default_content:
    - All notable changes to this project will be documented in this file.
    - The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
  git:
    commit: False
    commit_message: "[skip ci] Releasing Changelog version {new_version}"
    commit_additional_files: []
    tag: False
    tag_name: "v{new_version}"
    tag_description: "Version v{new_version} released"
  links:
    auto_generate: False
    compare_versions_template: '{host}/compare/{previous_version}...{version}'
    unreleased_changes_template: '{host}/compare/{latest_version}...master'
    initial_version_template: '{host}/tree/{version}'
  extension:
    post_release_version_prefix: null
  issue_tracker:
    jira:
      host: null
      username: null
      password: null
      issue_patterns: ["[A-Z]+-[0-9]+"]
      comment_template: |
        # 🚀 New version [v{new_version}]({link})

        A new release has been created referencing this issue. Please check it out.

        ## 🚧 Changes in this version

        {changes}

        ## 🧭 Reference

        Code: [Source Code Management System]({link})
  stash:
    directory: .kacl_stash
    always: False
```

You can customize any of these settings according to your project's needs. The configuration provides sensible defaults that work for most projects while offering extensive customization options for advanced use cases.

## Create a Changelog

```bash
Usage: kacl-cli new [OPTIONS]

  Creates a new changelog.

Options:
  -o, --output-file PATH  File to write the created changelog to.
  --help                  Show this message and exit.
```

**Usage**

```bash
kacl-cli new
```

Creates the following changelog

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
```

## Verify a Changelog

```
Usage: kacl-cli verify [OPTIONS]

  Verifies if the changelog is in "keep-a-changelog" format. Use '--json' get
  JSON formatted output that can be easier integrated into CI workflows.
  Exit code is the number of identified errors.

Options:
  --json  Print validation output as json
  --help  Show this message and exit.
```

**Usage**

```bash
kacl-cli verify
```

**JSON Output**

```bash
kacl-cli verify --json
```

```json
{
    "errors": [
        {
            "end_character_pos": 8,
            "error_message": "Versions need to be decorated with a release date in the following format 'YYYY-MM-DD'",
            "line": "## 1.0.0",
            "line_number": 8,
            "start_char_pos": 0
        },
        {
            "end_character_pos": 10,
            "error_message": "\"Hacked\" is not a valid section for a version. Options are [Added,Changed,Deprecated,Removed,Fixed,Security]",
            "line": "### Hacked",
            "line_number": 12,
            "start_char_pos": 4
        }
    ],
    "valid": false
}
```

## Print the current release version

**Usage**

```bash
kacl-cli current
```

```
0.1.2
```

## Print a single release changelog

**Usage**

```bash
kacl-cli get 0.2.2
```

```markdown
## [0.2.2] - 2018-01-16

### Added

- Many prior version. This was added as first entry in CHANGELOG when it was added to this project.
```

## Add an entry to an unreleased section

```
Usage: kacl-cli add [OPTIONS] SECTION MESSAGE

  Adds a given message to a specified unreleased section. A new unreleased
  section is added if it doesn't exist. Use '--modify' to directly modify
  the changelog file.

Options:
  -m, --modify  This option will add the changes directly into changelog file
  --help        Show this message and exit.
```

**Usage**

```bash
kacl-cli add fixed 'We fixed some bad issues' --modify
kacl-cli add added 'We just added some new cool stuff' --modify
kacl-cli add changed 'And changed things a bit' --modify
```

## Prepare a Changelog for a Release

```
Usage: kacl-cli release [OPTIONS] VERSION

  Creates a release for the latest 'unreleased' changes. Use '--modify' to
  directly modify the changelog file. You can automatically use the latest
  version by using the version keywords 'major', 'minor', 'patch', 'post'.
  Creates a new empty unreleased section if not disabled in the configuration
  file.

  Example:

      kacl-cli release 1.0.0

      kacl-cli release major|minor|patch

Options:
  -m, --modify            This option will add the changes directly into
                          changelog file.
  -l, --link TEXT         A url that the version will be linked with.
  -g, --auto-link         Will automatically create and update necessary
                          links.
  -c, --commit            If passed this will create a git commit with the
                          changed Changelog.
  --commit-message TEXT   The commit message to use when using --commit flag
  -t, --tag               If passed this will create a git tag for the newly
                          released version.
  --tag-name TEXT         The tag name to use when using --tag flag
  --tag-description TEXT  The tag description text to use when using --tag
                          flag
  -d, --allow-dirty       If passed this will allow to commit/tag even on a
                          "dirty".
  --help                  Show this message and exit.
```

**Git Support**

`kacl-cli` provides a direct integration into your git repository. When releasing you often want to directly commit and tag the changes you did.
Using the `release` command you can simply add the `--commit/--tag` option(s) that will add the changes made by the tool to git. These flags only take effect if you also provide
the `--modify` option, otherwise no change will happen to your file system. By specifying `--commit-message` and `--tag-description` you can also decide what kind of information you
want to see within the commit. Have a look at the _config_ section that shows more options to use along with the `release` command.

**Messages (--commit-message, --tag-name, --tag-description)**

This is templated using the Python Format String Syntax. Available in the template context are `latest_version` and `new_version` as well as all `environment variables` (prefixed with \$).
You can also use the variables `now` or `utcnow` to get a current timestamp. Both accept datetime formatting (when used like as in `{now:%d.%m.%Y}`).
Also available as --message (e.g.: kacl-cli release patch --commit --commit--message '[{now:%Y-%m-%d}] Jenkins Build {$BUILD_NUMBER}: {new_version}')

**Auto Link Generation**

`kacl-cli` can automatically generate links for every version for you. Using the `--auto-link` option will generate _version comparison_ links for you. The link generation can be configured using the _config_ file. See the config section for more details

```bash
kacl-cli release 1.0.0 --auto-link
```

Example output:

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2020-01-14
### Added
- `release` command will make sure changelog is valid before doing any changes.

## 0.2.16 - 2020-01-07
### Fixed
- fixed issue #3 that did not detect linked versions with missing links

[Unreleased]: https://gitlab.com/schmieder.matthias/python-kacl/tree/v1.0.0...HEAD
[1.0.0]: https://gitlab.com/schmieder.matthias/python-kacl/compare/v0.2.16...v1.0.0
```

**Usage with fixed version**

```bash
kacl-cli release 1.0.0
```

Example CHANGELOG.md (before):

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- added default content checks
- cli will now check for valid semantic version when using `release` command
- implemented basic cli with `new`, `get`, `release`, `verify`
- added `--json` option to `verify` command

## 0.1.0 - 2019-12-12
### Added
- initial release

[Unreleased]: https://gitlab.com/schmieder.matthias/python-kacl/compare/v1.0.0...HEAD
```

Example CHANGELOG.md (after):

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## 1.0.0 - 2019-12-22
### Added
- added default content checks
- cli will now check for valid semantic version when using `release` command
- implemented basic cli with `new`, `get`, `release`, `verify`
- added `--json` option to `verify` command

## 0.1.0 - 2019-12-12
### Added
- initial release

[Unreleased]: https://gitlab.com/schmieder.matthias/python-kacl/compare/v1.0.0...HEAD
```

**Usage with version increment**

```bash
kacl-cli release patch
```

Example CHANGELOG.md (after):

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## 0.1.1 - 2019-12-22
### Added
- added default content checks
- cli will now check for valid semantic version when using `release` command
- implemented basic cli with `new`, `get`, `release`, `verify`
- added `--json` option to `verify` command

## 0.1.0 - 2019-12-12
### Added
- initial release

[Unreleased]: https://gitlab.com/schmieder.matthias/python-kacl/compare/v1.0.0...HEAD
```

## Changelog Fragments

**kacl-cli** supports "changelog fragments" starting from version 6.6.0, which provides a powerful solution for managing unreleased changes in collaborative development environments. This feature helps avoid merge conflicts and simplifies changelog management when multiple developers are working on different branches simultaneously.

### Configuration

Enable changelog fragments through the `.kacl.yml` configuration file:

```yaml
kacl:
  stash:
    dir: .kacl_stash
    always: True
```

**Configuration Options:**

- `dir`: Directory where changelog fragments are stored (default: `.kacl_stash`)
- `always`: When `True`, all `kacl add` commands automatically create fragments instead of modifying the main changelog

### How It Works

The stash functionality stores "Unreleased" changes in separate fragment files within the configured stash directory. These fragment files are **git-branch aware**:

- **Inside a git repository**: Fragment files are named `{git_branch}.md`
- **Outside a git repository**: Fragment files use a timestamp-based name

This branch-aware naming ensures maximum segregation of changes, preventing merge conflicts and rebase issues that commonly occur when multiple merge requests modify the same changelog file simultaneously.

### Usage Patterns

#### Automatic Fragment Creation

With `always: True` in your configuration, all changelog additions are automatically directed to fragments:

```bash
kacl add -m Changed "my new changelog entry"
```

This command creates or updates a fragment file (e.g., `feature-branch.md`) instead of modifying the main `CHANGELOG.md`.

#### Manual Fragment Control

With `always: False`, you have explicit control over where changes are added:

```bash
# Add directly to CHANGELOG.md
kacl add -m Changed "directly to the CHANGELOG.md"

# Add to a fragment file
kacl add -m --stash Changed "into the fragment"
```

### Fragment Structure

Each fragment file contains a standard changelog structure:

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Changed
- my new changelog entry
```

### Release Integration

When executing `kacl release`, the system automatically:

1. **Collects all fragments** from the stash directory
2. **Merges fragment content** into the main changelog under the new release version
3. **Deletes processed fragments** from the stash directory
4. **Stages deletions in git** so fragments are removed when the release is committed

This seamless integration ensures that all distributed changes across branches are consolidated into a single release entry.

### Workflow Integration

Changelog fragments are fully integrated into all kacl workflows:

- **`kacl verify`**: Validates both the main changelog and all fragments
- **`kacl get`**: Considers fragment content when retrieving version information
- **Git operations**: Fragment cleanup is automatically handled during release commits

### Benefits

- **Eliminates merge conflicts** on changelog files
- **Enables parallel development** without coordination overhead
- **Maintains changelog quality** through individual fragment validation
- **Simplifies release process** with automatic fragment consolidation
- **Preserves git history** of changelog contributions per branch


## Link Generation

`kacl-cli` let's you easily generate links to your versions. You can automatically generate all links following the desired patterns using `kacl-cli link generate`.
The link generation can also be easily included into the `release` command and will take care of updating the `unreleased` and `latest_version` section.

```bash
Usage: kacl-cli link generate [OPTIONS]

Options:
  -m, --modify                    This option will add the changes directly
                                  into changelog file.
  --host-url TEXT                 Host url to the git service. (i.e
                                  https://gitlab.com/schmieder.matthias/python-kacl)
  --compare-versions-template TEXT
                                  Template string for version comparison link.
  --unreleased-changes-template TEXT
                                  Template string for unreleased changes link.
  --initial-version-template TEXT
                                  Template string for initial version link.
  --help                          Show this message and exit.
```

**Url Templating**

in order to generate the correct urls, `python-kacl` allows you to define three templates `compare-versions-template`, `unreleased-changes-template` and `initial-version-template` that can be used to tell the system how to generate proper links. The easiest way to provide this information is to pass it to the `.kacl.yml` config file

```yaml
kacl:
  links:
    # The host url is optional and will be automatically determined using your git repository. If run on gitlab CI the host will be determined by CI_PROJECT_URL if not specified here.
    host_url: https://github.com/mschmieder/kacl-cli
    compare_versions_template: '{host}/compare/v{previous_version}...v{version}'
    unreleased_changes_template: '{host}/compare/v{latest_version}...HEAD'
    initial_version_template: '{host}/tree/v{version}'
```

Using the python format syntax you can generate any links you want. The available replacement variables are `version`, `previous_version`, `host` and `latest_version`.

## Squashing releases

If you are follwing a automated versioning approach, you will often times create a number of versions that might clutter Changelog. For this purpose, `kacl-cli` provides a `squash` command that let's you squash releases into a single one without loosing valuable information.

To squash the versions, you will need to specify the version range to squash by passing `--from-version` and `--to-version` to `kacl-cli squash`. Strings passed need to be valid Semantic Versions.

```bash
Usage: kacl-cli squash [OPTIONS]

  Squshes all changes from a given version into a single section. Use '--
  modify' to directly modify the changelog file.

Options:
  -m, --modify         This option will add the changes directly into
                       changelog file.
  --from-version TEXT  The version to start squashing from.  [required]
  --to-version TEXT    The version to squash to. If not given, the latest
                       version will be used.
  --help               Show this message and exit.
```

### Example

```bash
kacl-cli -f CHANGELOG.md squash \
  --from-version "0.0.1" \
  --from-version "1.0.0" \
  --modify
```

This example will squash all versions between `0.0.1` and `1.0.0` and move them under `1.0.0`

## Issue Management Integration

With `python-kacl >= 0.6.0`, you can integrate changelog and release management directly into your Issue Management System. Currently, the supported system is JIRA.

It is common practice to reference fixed or addressed issues in the changelog, as shown below:

```markdown
## Unreleased
### Added
- JIRA-1754 Just unreleased stuff

## 1.0.0 - 2017-06-20
### Added
- JIRA-9: added UI functionality

### Fixed
- issue JIRA-13 closed by applying the solution
```

### Adding Comments to Issues

The `add-comments` command allows you to detect issue IDs using a custom pattern and create comments in the Issue Tracking system about a new release.

You can pass all necessary arguments via CLI or set up your `.kacl.yaml` configuration file. The following options are available:

```yaml
issue_tracker:
  jira:
    host: jira.atlassian.com # The host name of your JIRA instance
    username: null # The username to login. Uses JIRA_USERNAME environment variable if available
    password: null # The password to login. Uses JIRA_PASSWORD environment variable if available
    issue_patterns: # List of regex patterns to identify the issues
      - "[A-Z]+-[0-9]+"
      - "JIRA-[0-9]+"
    comment_template: | # A text template used to comment on the issue
      # 🚀 New version [v{new_version}]({link})

      A new release has been created referencing this issue. Please check it out.

      ## 🚧 Changes in this version

      {changes}

      ## 🧭 Reference

      Code: [Source Code Management System]({link})
```

Run the following command to create the comments:

```bash
kacl-cli add-comments 1.0.0
```

### Command Options

See all available command options:

```bash
Usage: kacl-cli add-comments [OPTIONS] VERSION

  Adds comments to issues identified within the CHANGELOG. Currently
  supported system: JIRA

Options:
  --jira-username TEXT          JIRA username. Will also look for the
                                JIRA_USERNAME environment variable.
  --jira-password TEXT          JIRA password. Will also look for the
                                JIRA_PASSWORD environment variable.
  --jira-host TEXT              JIRA host. Will also look for the JIRA_HOST
                                environment variable.
  --jira-issue-pattern TEXT     Issue pattern to search the changelog for. Can
                                be specified multiple times.
  --jira-comment-template TEXT  JIRA comment template.
  --fail                        Fail if comments could not be added.
  --help                        Show this message and exit.
```

### Templating the Comment

The `comment_template` parameter allows various templating options. The following template variables are available:

| Variable       | Description                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| `new_version`  | The version that was just released                                                                    |
| `changes`      | The markdown content within the change section of your CHANGELOG                                      |
| `link`         | The link to the version within your source code management system according to the link configuration |
| `env.MYENVVAR` | Any environment variable                                                                              |

This flexibility allows you to adapt the comment patterns to your needs and dynamically create them. For example, adding CI/CD information can be easily achieved as follows:

```yaml
comment_template: | # A text template used to comment on the issue
    # 🚀 New version [v{new_version}]({link})

    A new release has been created referencing this issue. Please check it out.

    ## 🚧 Changes in this version

    {changes}

    ## 🧭 Reference

    Code: [Source Code Management System]({link})
    Pipeline: [Pipeline ({env.CI_PIPELINE_IID})]({env.CI_PIPELINE_URL})
    GitLab Project: [({env.CI_PROJECT_TITLE})]({env.CI_PROJECT_URL})
```

## Extensions

### Post-release/Hotfix

> **ATTENTION:** this is not SemVer compatible and not part of the KACL standard

In some situations you might come across the challenge to patch a piece of software that is already in production and you _have to_ indicate that this is a `hotfix` release. `SemVer` is not meant to support this other than incrementing the `patch` version of your project, but it is not possible to release `1.0.1-hotfix.1` after `1.0.1` as `-hotfix.1` is considered a `prerelease` version and therefore is lower in order than the `1.0.1` version.

To overcome this, `kacl` provides an `extension` to you can use in such corner cases

You can enable the `post-release` extension by providing the `post_release_version_prefix` within the `extension` secion of your config file. By setting `post_release_version_prefix: hotfix` you can now easily release `hotfix` versions that are considered of higher order than the base version

```yaml
kacl:
  extension:
    post_release_version_prefix: hotfix
```

```bash

# get current version
kacl-cli current
>> 0.3.1

# add another change
kacl-cli add Security "Security Hotfix" -m

# release a hotfix version
kacl-cli release post -m

# get current version
kacl-cli current
>> 0.3.1-hotfix.1
```

## Config file

`kacl-cli` will automatically check if there is a `.kacl.yml` present within your execution directory. Within this configuration file you can set options to improve
specifically CI workflows. It also allows you to better customize the validation behaviour of the system by allowing to define _custom header titles_, _allowed_version_sections_ as well as the
required _default content_.

By specifying a `.kacl.yml` with any of those options, the _default config_ will be merged with those local changes. Most options are also available on the CLI which take precedence over the ones
within the config files.

### Default Config

```yaml
kacl:
  file: CHANGELOG.md
  allowed_header_titles:
    - Changelog
    - Change Log
  allowed_version_sections:
    - Added
    - Changed
    - Deprecated
    - Removed
    - Fixed
    - Security
  default_content:
    - All notable changes to this project will be documented in this file.
    - The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
  release:
    add_unreleased: True
  git:
    commit: False
    commit_message: "[skip ci] Releasing Changelog version {new_version}"
    commit_additional_files: []
    tag: False
    tag_name: "v{new_version}"
    tag_description: "Version v{new_version} released"
  links:
    auto_generate: False
    compare_versions_template: '{host}/compare/{previous_version}...{version}'
    unreleased_changes_template: '{host}/compare/{latest_version}...master'
    initial_version_template: '{host}/tree/{version}'
  extension:
    post_release_version_prefix: null
  issue_tracker:
    jira:
      host: null
      username: null
      password: null
      issue_patterns: ["[A-Z]+-[0-9]+"]
      comment_template: |
        # 🚀 New version [v{new_version}]({link})

        A new release has been created referencing this issue. Please check it out.

        ## 🚧 Changes in this version

        {changes}

        ## 🧭 Reference

        Code: [Source Code Management System]({link})
  stash:
    directory: .kacl_stash
    always: False
```

### Configuration Parameters

| Parameter                               | Type    | Default                                                              | Description                                              |
| --------------------------------------- | ------- | -------------------------------------------------------------------- | -------------------------------------------------------- |
| **Basic Settings**                      |         |                                                                      |                                                          |
| `file`                                  | string  | `CHANGELOG.md`                                                       | Path to the changelog file                               |
| `allowed_header_titles`                 | array   | `["Changelog", "Change Log"]`                                        | Valid changelog header titles                            |
| `allowed_version_sections`              | array   | `["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]` | Valid section names within version entries               |
| `default_content`                       | array   | See default config                                                   | Default content lines for new changelog files            |
| **Git Integration**                     |         |                                                                      |                                                          |
| `git.commit`                            | boolean | `false`                                                              | Automatically commit changelog changes during release    |
| `git.commit_message`                    | string  | `"[skip ci] Releasing Changelog version {new_version}"`              | Template for commit messages                             |
| `git.commit_additional_files`           | array   | `[]`                                                                 | Additional files to include in release commits           |
| `git.tag`                               | boolean | `false`                                                              | Automatically create git tags during release             |
| `git.tag_name`                          | string  | `"v{new_version}"`                                                   | Template for git tag names                               |
| `git.tag_description`                   | string  | `"Version v{new_version} released"`                                  | Template for git tag descriptions                        |
| **Release Settings**                    |         |                                                                      |                                                          |
| `release.add_unreleased`                | boolean | `true`                                                               | Automatically add new "Unreleased" section after release |
| **Link Generation**                     |         |                                                                      |                                                          |
| `links.auto_generate`                   | boolean | `false`                                                              | Automatically generate version links during release      |
| `links.compare_versions_template`       | string  | `"{host}/compare/{previous_version}...{version}"`                    | Template for version comparison links                    |
| `links.unreleased_changes_template`     | string  | `"{host}/compare/{latest_version}...master"`                         | Template for unreleased changes links                    |
| `links.initial_version_template`        | string  | `"{host}/tree/{version}"`                                            | Template for initial version links                       |
| **Extensions**                          |         |                                                                      |                                                          |
| `extension.post_release_version_prefix` | string  | `null`                                                               | Prefix for post-release/hotfix versions (non-SemVer)     |
| **Issue Tracker Integration**           |         |                                                                      |                                                          |
| `issue_tracker.jira.host`               | string  | `null`                                                               | JIRA instance hostname (also reads `JIRA_HOST` env var)  |
| `issue_tracker.jira.username`           | string  | `null`                                                               | JIRA username (also reads `JIRA_USERNAME` env var)       |
| `issue_tracker.jira.password`           | string  | `null`                                                               | JIRA password (also reads `JIRA_PASSWORD` env var)       |
| `issue_tracker.jira.issue_patterns`     | array   | `["[A-Z]+-[0-9]+"]`                                                  | Regex patterns to identify issue references in changelog |
| `issue_tracker.jira.comment_template`   | string  | See default config                                                   | Template for comments posted to JIRA issues              |
| **Changelog Fragments**                 |         |                                                                      |                                                          |
| `stash.directory`                       | string  | `.kacl_stash`                                                        | Directory for storing changelog fragments                |
| `stash.always`                          | boolean | `false`                                                              | Always use fragments instead of modifying main changelog |

### Template Variables

The following variables are available for templating in commit messages, tag names, descriptions, and JIRA comments:

| Variable             | Description                       | Example                        |
| -------------------- | --------------------------------- | ------------------------------ |
| `{new_version}`      | The version being released        | `1.2.3`                        |
| `{latest_version}`   | The previous version              | `1.2.2`                        |
| `{previous_version}` | Same as latest_version            | `1.2.2`                        |
| `{host}`             | Git repository host URL           | `https://github.com/user/repo` |
| `{changes}`          | Changelog content for the version | Markdown content               |
| `{link}`             | Link to the version in SCM        | Generated link URL             |
| `{env.VAR_NAME}`     | Environment variable              | Value of `VAR_NAME`            |

## Development

With these instructions you can easily setup a development environment

```bash
# clone the project
git clone https://gitlab.com/schmieder.matthias/python-kacl
cd python-kacl

# create a virtual env
python3 -m venv .venv
source ./.venv/bin/activate

# install in development mode
pip install -e .

# install development requirements
pip install -r dev-requirements.txt

# run the tests
python3 -m pytest --snapshot-update --allow-snapshot-deletion

# open VSCode
code .
```
