That's correct, at least for linking existing material and, overall, providing and overview of the project and the (now many) components.

As for the "CONTRIBUTING" document, I will prepare something inspired by [this](), according to these [general guidelines](https://mozillascience.github.io/working-open-workshop/contributing/).

# Contributing to CoderBot

:+1::robot: Thanks for your interest in the CoderBot project! :robot::+1:

The following is a set of guidelines for contributing to CoderBot and its modules, which are hosted in the [CoderBot Organization](https://github.com/CoderBotOrg) on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[What should I know before I get started?](#what-should-i-know-before-i-get-started)
  * [CoderBot project description](#coderbot-project-description)
  * [CoderBot architecture](#coderbot-architecture)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [JavaScript Styleguide](#javascript-styleguide)
  * [CoffeeScript Styleguide](#coffeescript-styleguide)
  * [Specs Styleguide](#specs-styleguide)
  * [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Code of Conduct

This project and everyone participating in it is governed by the [CoderBot Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [info@coderbot.org](info@coderbot.org).

## What should I know before I get started?

### CoderBot project description

CoderBot is an open source project  with the objective of providing the hardware and software used in the educational robot with the same name. 

It is composed by several [repositories](https://github.com/CoderBotOrg). When you initially consider contributing to CoderBot, you might be unsure about which of those repositories implements the functionality you want to change or report a bug for. This section should help you with that.

#### Package Conventions

### CoderBot architecture

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for CoderBot. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](https://github.com/CoderBotOrg/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.md), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### Before Submitting A Bug Report

* TODO

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). After you've determined [which repository](#coderbot-and-repos) your bug is related to, create an issue on that repository and provide the following information by filling in [the template](https://github.com/CoderBotOrg/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.md).

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible.

Provide more context by answering these questions:

° TODO

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for CoderBot, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in [the template](https://github.com/CoderBotOrg/.github/blob/master/.github/ISSUE_TEMPLATE/feature_request.md), including the steps that you imagine you would take if the feature you're requesting existed.

#### Before Submitting An Enhancement Suggestion

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). After you've determined [which repository](#coderbot-and-repos) your enhancement suggestion is related to, create an issue on that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples, as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** to most CoderBot users and isn't something that can or should be implemented as a [community package](#coderbot-and-repos).
* **List some other text editors or applications where this enhancement exists.**

### Your First Code Contribution

Unsure where to begin contributing to CoderBot? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues][beginner] - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `beginner` issues.

Both issue lists are sorted by total number of comments. While not perfect, number of comments is a reasonable proxy for impact a given change will have.

#### Local development

* TODO

### Pull Requests

The process described here has several goals:

- Maintain CoderBot's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible CoderBot
- Enable a sustainable system for CoderBot's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing <details><summary>What if the status checks are failing?</summary>If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe the failure is unrelated. A maintainer will re-run the status check for you. If we conclude that the failure was a false positive, then we will open an issue to track that problem with our status check suite.</details>

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* When only changing documentation, include `[ci skip]` in the commit title

### JavaScript Styleguide

All JavaScript code is linted with [Prettier](https://prettier.io/).

* Prefer the object spread operator (`{...anotherObj}`) to `Object.assign()`
* Inline `export`s with expressions whenever possible
  ```js
  // Use this:
  export default class ClassName {

  }

  // Instead of:
  class ClassName {

  }
  export default ClassName
  ```
* Place requires in the following order:
    * Built in Node Modules (such as `path`)    
    * Local Modules (using relative paths)
* Place class properties in the following order:
    * Class methods and properties (methods starting with `static`)
    * Instance methods and properties

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Reference methods and classes in markdown with the custom `{}` notation:
    * Reference classes with `{ClassName}`
    * Reference instance methods with `{ClassName::methodName}`
    * Reference class methods with `{ClassName.methodName}`

#### Example

* TODO

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests. Most labels are used across all CoderBot repositories.

[GitHub search](https://help.github.com/articles/searching-issues/) makes it easy to use labels for finding groups of issues or pull requests you're interested in. 
The labels are loosely grouped by their purpose, but it's not required that every issue has a label from every group or that an issue can't have more than one label from the same group.

#### Type of Issue and Issue State

| Label name | `CoderBotOrg` :mag_right: | `CoderBot`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `enhancement` | [search][search-coderbot-repo-label-enhancement] | [search][search-coderbot-org-label-enhancement] | Feature requests. |
| `bug` | [search][search-coderbot-repo-label-bug] | [search][search-coderbot-org-label-bug] | Confirmed bugs or reports that are very likely to be bugs. |
| `question` | [search][search-coderbot-repo-label-question] | [search][search-coderbot-org-label-question] | Questions more than bug reports or feature requests (e.g. how do I do X). |
| `feedback` | [search][search-coderbot-repo-label-feedback] | [search][search-coderbot-org-label-feedback] | General feedback more than bug reports or feature requests. |
| `help-wanted` | [search][search-coderbot-repo-label-help-wanted] | [search][search-coderbot-org-label-help-wanted] | The CoderBot core team would appreciate help from the community in resolving these issues. |
| `beginner` | [search][search-coderbot-repo-label-beginner] | [search][search-coderbot-org-label-beginner] | Less complex issues which would be good first issues to work on for users who want to contribute to CoderBot. |
| `more-information-needed` | [search][search-coderbot-repo-label-more-information-needed] | [search][search-coderbot-org-label-more-information-needed] | More information needs to be collected about these problems or feature requests (e.g. steps to reproduce). |
| `needs-reproduction` | [search][search-coderbot-repo-label-needs-reproduction] | [search][search-coderbot-org-label-needs-reproduction] | Likely bugs, but haven't been reliably reproduced. |
| `blocked` | [search][search-coderbot-repo-label-blocked] | [search][search-coderbot-org-label-blocked] | Issues blocked on other issues. |
| `duplicate` | [search][search-coderbot-repo-label-duplicate] | [search][search-coderbot-org-label-duplicate] | Issues which are duplicates of other issues, i.e. they have been reported before. |
| `wontfix` | [search][search-coderbot-repo-label-wontfix] | [search][search-coderbot-org-label-wontfix] | The CoderBot core team has decided not to fix these issues for now, either because they're working as intended or for some other reason. |
| `invalid` | [search][search-coderbot-repo-label-invalid] | [search][search-coderbot-org-label-invalid] | Issues which aren't valid (e.g. user errors). |
| `package-idea` | [search][search-coderbot-repo-label-package-idea] | [search][search-coderbot-org-label-package-idea] | Feature request which might be good candidates for new packages, instead of extending CoderBot or core CoderBot packages. |
| `wrong-repo` | [search][search-coderbot-repo-label-wrong-repo] | [search][search-coderbot-org-label-wrong-repo] | |

#### Topic Categories

| Label name | `CoderBotOrg/backend` :mag_right: | `CoderBotOrg`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `windows` | [search][search-coderbot-repo-label-windows] | [search][search-coderbot-org-label-windows] | Related to CoderBot running on Windows. |
| `linux` | [search][search-coderbot-repo-label-linux] | [search][search-coderbot-org-label-linux] | Related to CoderBot running on Linux. |
| `mac` | [search][search-coderbot-repo-label-mac] | [search][search-coderbot-org-label-mac] | Related to CoderBot running on macOS. |
| `documentation` | [search][search-coderbot-repo-label-documentation] | [search][search-coderbot-org-label-documentation] | Related to any type of documentation (e.g. [API documentation]() and the [flight manual]()). |
| `performance` | [search][search-coderbot-repo-label-performance] | [search][search-coderbot-org-label-performance] | Related to performance. |
| `security` | [search][search-coderbot-repo-label-security] | [search][search-coderbot-org-label-security] | Related to security. |
| `ui` | [search][search-coderbot-repo-label-ui] | [search][search-coderbot-org-label-ui] | Related to visual design. |
| `api` | [search][search-coderbot-repo-label-api] | [search][search-coderbot-org-label-api] | Related to CoderBot's public APIs. |
| `uncaught-exception` | [search][search-coderbot-repo-label-uncaught-exception] | [search][search-coderbot-org-label-uncaught-exception] | Issues about uncaught exceptions. |
| `crash` | [search][search-coderbot-repo-label-crash] | [search][search-coderbot-org-label-crash] | Reports of CoderBot completely crashing. |
| `auto-indent` | [search][search-coderbot-repo-label-auto-indent] | [search][search-coderbot-org-label-auto-indent] | Related to auto-indenting text. |
| `encoding` | [search][search-coderbot-repo-label-encoding] | [search][search-coderbot-org-label-encoding] | Related to character encoding. |
| `network` | [search][search-coderbot-repo-label-network] | [search][search-coderbot-org-label-network] | Related to network problems or working with remote files (e.g. on network drives). |
| `git` | [search][search-coderbot-repo-label-git] | [search][search-coderbot-org-label-git] | Related to Git functionality (e.g. problems with gitignore files or with showing the correct file status). |

#### `CoderBotOrg/backend` Topic Categories

| Label name | `CoderBotOrg/backend` :mag_right: | `CoderBotOrg`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `editor-rendering` | [search][search-coderbot-repo-label-editor-rendering] | [search][search-coderbot-org-label-editor-rendering] | Related to language-independent aspects of rendering text (e.g. scrolling, soft wrap, and font rendering). |
| `build-error` | [search][search-coderbot-repo-label-build-error] | [search][search-coderbot-org-label-build-error] | Related to problems with building CoderBot from source. |
| `error-from-pathwatcher` | [search][search-coderbot-repo-label-error-from-pathwatcher] | [search][search-coderbot-org-label-error-from-pathwatcher] | |
| `error-from-save` | [search][search-coderbot-repo-label-error-from-save] | [search][search-coderbot-org-label-error-from-save] | Related to errors thrown when saving files. |
| `error-from-open` | [search][search-coderbot-repo-label-error-from-open] | [search][search-coderbot-org-label-error-from-open] | Related to errors thrown when opening files. |
| `installer` | [search][search-coderbot-repo-label-installer] | [search][search-coderbot-org-label-installer] | Related to the CoderBot installers for different OSes. |
| `auto-updater` | [search][search-coderbot-repo-label-auto-updater] | [search][search-coderbot-org-label-auto-updater] | Related to the auto-updater for different OSes. |
| `deprecation-help` | [search][search-coderbot-repo-label-deprecation-help] | [search][search-coderbot-org-label-deprecation-help] | Issues for helping package authors remove usage of deprecated APIs in packages. |
| `electron` | [search][search-coderbot-repo-label-electron] | [search][search-coderbot-org-label-electron] |  |

#### Pull Request Labels

| Label name | `CoderBotOrg/backend` :mag_right: | `CoderBotOrg`‑org :mag_right: | Description
| --- | --- | --- | --- |
| `work-in-progress` | [search][search-coderbot-repo-label-work-in-progress] | [search][search-coderbot-org-label-work-in-progress] | Pull requests which are still being worked on, more changes will follow. |
| `needs-review` | [search][search-coderbot-repo-label-needs-review] | [search][search-coderbot-org-label-needs-review] | Pull requests which need code review, and approval from maintainers or CoderBot core team. |
| `under-review` | [search][search-coderbot-repo-label-under-review] | [search][search-coderbot-org-label-under-review] | Pull requests being reviewed by maintainers or CoderBot core team. |
| `requires-changes` | [search][search-coderbot-repo-label-requires-changes] | [search][search-coderbot-org-label-requires-changes] | Pull requests which need to be updated based on review comments and then reviewed again. |
| `needs-testing` | [search][search-coderbot-repo-label-needs-testing] | [search][search-coderbot-org-label-needs-testing] | Pull requests which need manual testing. |

[search-coderbot-repo-label-enhancement]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aenhancement
[search-coderbot-org-label-enhancement]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aenhancement
[search-coderbot-repo-label-bug]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Abug
[search-coderbot-org-label-bug]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Abug
[search-coderbot-repo-label-question]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aquestion
[search-coderbot-org-label-question]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aquestion
[search-coderbot-repo-label-feedback]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Afeedback
[search-coderbot-org-label-feedback]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Afeedback
[search-coderbot-repo-label-help-wanted]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Ahelp-wanted
[search-coderbot-org-label-help-wanted]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Ahelp-wanted
[search-coderbot-repo-label-beginner]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Abeginner
[search-coderbot-org-label-beginner]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Abeginner
[search-coderbot-repo-label-more-information-needed]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Amore-information-needed
[search-coderbot-org-label-more-information-needed]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Amore-information-needed
[search-coderbot-repo-label-needs-reproduction]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aneeds-reproduction
[search-coderbot-org-label-needs-reproduction]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aneeds-reproduction
[search-coderbot-repo-label-triage-help-needed]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Atriage-help-needed
[search-coderbot-org-label-triage-help-needed]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Atriage-help-needed
[search-coderbot-repo-label-windows]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Awindows
[search-coderbot-org-label-windows]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Awindows
[search-coderbot-repo-label-linux]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Alinux
[search-coderbot-org-label-linux]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Alinux
[search-coderbot-repo-label-mac]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Amac
[search-coderbot-org-label-mac]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Amac
[search-coderbot-repo-label-documentation]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Adocumentation
[search-coderbot-org-label-documentation]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Adocumentation
[search-coderbot-repo-label-performance]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aperformance
[search-coderbot-org-label-performance]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aperformance
[search-coderbot-repo-label-security]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Asecurity
[search-coderbot-org-label-security]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Asecurity
[search-coderbot-repo-label-ui]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aui
[search-coderbot-org-label-ui]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aui
[search-coderbot-repo-label-api]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aapi
[search-coderbot-org-label-api]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aapi
[search-coderbot-repo-label-crash]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Acrash
[search-coderbot-org-label-crash]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Acrash
[search-coderbot-repo-label-auto-indent]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aauto-indent
[search-coderbot-org-label-auto-indent]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aauto-indent
[search-coderbot-repo-label-encoding]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aencoding
[search-coderbot-org-label-encoding]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aencoding
[search-coderbot-repo-label-network]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Anetwork
[search-coderbot-org-label-network]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Anetwork
[search-coderbot-repo-label-uncaught-exception]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Auncaught-exception
[search-coderbot-org-label-uncaught-exception]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Auncaught-exception
[search-coderbot-repo-label-git]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Agit
[search-coderbot-org-label-git]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Agit
[search-coderbot-repo-label-blocked]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Ablocked
[search-coderbot-org-label-blocked]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Ablocked
[search-coderbot-repo-label-duplicate]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aduplicate
[search-coderbot-org-label-duplicate]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aduplicate
[search-coderbot-repo-label-wontfix]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Awontfix
[search-coderbot-org-label-wontfix]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Awontfix
[search-coderbot-repo-label-invalid]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Ainvalid
[search-coderbot-org-label-invalid]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Ainvalid
[search-coderbot-repo-label-package-idea]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Apackage-idea
[search-coderbot-org-label-package-idea]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Apackage-idea
[search-coderbot-repo-label-wrong-repo]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Awrong-repo
[search-coderbot-org-label-wrong-repo]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Awrong-repo
[search-coderbot-repo-label-editor-rendering]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aeditor-rendering
[search-coderbot-org-label-editor-rendering]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aeditor-rendering
[search-coderbot-repo-label-build-error]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Abuild-error
[search-coderbot-org-label-build-error]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Abuild-error
[search-coderbot-repo-label-error-from-pathwatcher]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aerror-from-pathwatcher
[search-coderbot-org-label-error-from-pathwatcher]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aerror-from-pathwatcher
[search-coderbot-repo-label-error-from-save]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aerror-from-save
[search-coderbot-org-label-error-from-save]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aerror-from-save
[search-coderbot-repo-label-error-from-open]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aerror-from-open
[search-coderbot-org-label-error-from-open]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aerror-from-open
[search-coderbot-repo-label-installer]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Ainstaller
[search-coderbot-org-label-installer]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Ainstaller
[search-coderbot-repo-label-auto-updater]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Aauto-updater
[search-coderbot-org-label-auto-updater]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aauto-updater
[search-coderbot-repo-label-deprecation-help]: https://github.com/search?q=is%3Aopen+is%3Aissue+repo%3ACoderBotOrg%2Fbackend+label%3Adeprecation-help
[search-coderbot-org-label-deprecation-help]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Adeprecation-help
[search-coderbot-repo-label-electron]: https://github.com/search?q=is%3Aissue+repo%3ACoderBotOrg%2Fbackend+is%3Aopen+label%3Aelectron
[search-coderbot-org-label-electron]: https://github.com/search?q=is%3Aopen+is%3Aissue+user%3ACoderBotOrg+label%3Aelectron
[search-coderbot-repo-label-work-in-progress]: https://github.com/search?q=is%3Aopen+is%3Apr+repo%3ACoderBotOrg%2Fbackend+label%3Awork-in-progress
[search-coderbot-org-label-work-in-progress]: https://github.com/search?q=is%3Aopen+is%3Apr+user%3ACoderBotOrg+label%3Awork-in-progress
[search-coderbot-repo-label-needs-review]: https://github.com/search?q=is%3Aopen+is%3Apr+repo%3ACoderBotOrg%2Fbackend+label%3Aneeds-review
[search-coderbot-org-label-needs-review]: https://github.com/search?q=is%3Aopen+is%3Apr+user%3ACoderBotOrg+label%3Aneeds-review
[search-coderbot-repo-label-under-review]: https://github.com/search?q=is%3Aopen+is%3Apr+repo%3ACoderBotOrg%2Fbackend+label%3Aunder-review
[search-coderbot-org-label-under-review]: https://github.com/search?q=is%3Aopen+is%3Apr+user%3ACoderBotOrg+label%3Aunder-review
[search-coderbot-repo-label-requires-changes]: https://github.com/search?q=is%3Aopen+is%3Apr+repo%3ACoderBotOrg%2Fbackend+label%3Arequires-changes
[search-coderbot-org-label-requires-changes]: https://github.com/search?q=is%3Aopen+is%3Apr+user%3ACoderBotOrg+label%3Arequires-changes
[search-coderbot-repo-label-needs-testing]: https://github.com/search?q=is%3Aopen+is%3Apr+repo%3ACoderBotOrg%2Fbackend+label%3Aneeds-testing
[search-coderbot-org-label-needs-testing]: https://github.com/search?q=is%3Aopen+is%3Apr+user%3ACoderBotOrg+label%3Aneeds-testing

[beginner]:https://github.com/search?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abeginner+label%3Ahelp-wanted+user%3ACoderBotOrg+sort%3Acomments-desc
[help-wanted]:https://github.com/search?q=is%3Aopen+is%3Aissue+label%3Ahelp-wanted+user%3ACoderBotOrg+sort%3Acomments-desc+-label%3Abeginner
[contributing-to-official-coderbot-packages]: todo
[hacking-on-coderbot-core]: todo

