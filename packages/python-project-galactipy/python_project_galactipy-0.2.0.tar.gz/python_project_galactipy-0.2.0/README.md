# Python Project

<div align="center">

<!-- Project details -->
[![Python support][bp1]][bp2]
[![PyPI Release][bp3]][bp2]
[![Repository][bscm1]][bp4]
[![Releases][bscm2]][bp5]
[![Docker][bdocker1]][bdocker2]
[![Licence][blic1]][blic2]
[![Expand your project structure from atoms of code to galactic dimensions.][bp6]][bp7]

<!-- Information on development -->
[![Contributions Welcome][bp8]][bp9]
[![Open issues][bscm3]][bp10]
[![Merge Requests][bscm4]][bscm5]

<!-- Styling policies -->
[![BDD][bbbd1]][bbbd2]
[![Code style: Ruff][bfo1]][bfo2]
[![Docstrings][bli1]][bli2]
[![Gitmoji][bcv1]][bcv2]
[![Semantic Line Breaks][bp11]][bp12]

<!-- Development utilities -->
[![Poetry][bp13]][bp14]
[![Pre-commit][bp15]][bp16]
[![Bandit][bp17]][bp18]
[![isort][bfo3]][bfo4]
[![Editorconfig][bp19]][bp20]

<!-- Open Source benchmarks -->
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![OpenSSF Best Practices][boss1]][boss2] -->
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![OSSRank][boss3]][boss4] -->

<!-- Quality assurance -->
[![Semantic versions][bp21]][bp5]
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![Code Quality][bcov1]][bcov2] -->
<!-- UPDATEME by toggling this comment off after replacing your project's index in both anchors below
[![Coverage][bcov3]][bcov4] -->
[![Pipelines][bscm6]][bscm7]

_Awesome `python-project` is a Python cli/package created with https://gitlab.com/galactipy/galactipy_

</div>

## Very first steps

### Initialize your code

1. Initialize `git` inside your repo:

```bash
cd python-project && git init
```

2. If you don't have `Poetry` installed run:

```bash
invoke poetry-download
```

> This installs Poetry as a [standalone application][fs1]. If you prefer, install it through your distribution's package manager.

3. Initialize Poetry and install `pre-commit` hooks:

```bash
invoke install
invoke pre-commit-install
```

4. Run the codestyle:

```bash
invoke codestyle
```

5. Upload initial code to GitLab:

```bash
git add .
git commit -m ":tada: Initial commit"
git branch -M main
git remote add origin https://gitlab.com/galactipy/python-project.git
git push -u origin main
```

### Set up bots

- Set up a [Repository Access Token][lab1] to enable automatic releases and issue closing.


### Poetry

Want to know more about Poetry? Check [its documentation][fs2].

<details>
<summary>Details about Poetry</summary>
<p>

Poetry's [commands][fs3] are very intuitive and easy to learn, like:

- `poetry add numpy@latest`
- `poetry run pytest`
- `poetry publish --build`

etc.
</p>
</details>

### Building and releasing your package

In order to release a new version of the application, a few steps are needed.

Make sure you have a PyPI account and generate an API token, you can then register it in your repository with

```bash
invoke pypi-config <API_token>
```

Then, you're all good to build and publish your package in one go!

```bash
invoke publish
```

You should also [push a tag][fs5] to `GitLab` or `GitHub` and create a `Release` for your application on the platform to ensure users can check the latest version contents.

Of course, you can also rely solely on the CI tools provided by Galactipy to handle building, publishing and releasing automatically, with minimal configuration required! :partying_face:

Pushing a tag to your repository will also set up the automated workflows to build and publish your image to the GitLab Container Registry.

## :dart: What's next

Well, that's up to you. :muscle:

For further setting up your project:

- [ ] Look for files and sections marked with `TODO` (which must be addressed in order for your project to run properly) and `UPDATEME` (optional settings if you feel inclined to);
  - If you use VS Code, install the [`Todo Tree`][wn1] extension to easily locate and jump to these marks, they are already configured in your `settings.json` file;
- [ ] Make sure to create your desired Issue labels on your platform before you start tracking them so it ensures you will be able to filter them from the get-go;
- [ ] Make changes to your CI configurations to better suit your needs.

- In order to reduce user prompts and keep things effective, the template generates files with a few assumptions:
  - It assumes your main git branch is `master`. If you wish to use another branch name for development, be aware of changes you will have to make in the Issue and Merge Request templates and `README.md` file so links won't break when you push them to your repo;
  - It generates a PyPI badge assuming you will be able to publish your project under `python-project`, change it otherwise;
  - It assumes you will be pushing container images to the GitLab Container Registry at `galactipy/python-project`, change it otherwise.

If you want to put your project on steroids, here are a few Python tools which can help you depending on what you want to achieve with your application:

- [`Typer`][wn2] is great for creating CLI applications;
- [`Textual`][wn3] allows you to create more advanced terminal applications, such as a text editor or even your own shell;
- [`Rich`][wn4] makes it easy to add beautiful formatting in the terminal;
- [`tqdm`][wn5] is a fast, extensible progress bar for Python and CLI;
- [`orjson`][wn6], an ultra fast JSON parsing library;
- [`Pydantic`][wn7] is data validation and settings management using Python type hinting;
- [`Returns`][wn8] makes you function's output meaningful, typed, and safe;
- [`Loguru`][wn9] makes logging (stupidly) simple;
- [`IceCream`][wn10] is a little library for sweet and creamy debugging;
- [`Hydra`][wn11] is a framework for elegantly configuring complex applications;
- [`FastAPI`][wn12] is a type-driven asynchronous web framework.

For taking development and exposition of your project to the next level:

- Try out some more badges, not only it looks good, but it also helps people better understand some intricate details on how your project works:
  - You can look at dynamic badges available at [`Shields.io`][wn13];
  - There is a myriad of standardised static badges at [`Simple Badges`][wn14];
  - [`awesome-badges`][wn15] provides a lot of useful resources to help you deal with badges;
- Setup a code coverage service for your tests, popular options include:
  - [`Coveralls`][wn18] and [`Codecov`][wn19] if you need solely test coverage;
  - [`Code Climate`][wn20] and [`Codacy`][wn21] for fully-featured code analysis;
- Add your project to [`OpenSSF Best Practices`][wno1] and [`OSSRank`][wno2] indexes. If you have greater ambitions for your project and/or expects it to scale at some point, it's worth considering adding it to these trackers;
  - There are already badges for those set up in your `README.md` file, just waiting for you to update their URLs with your project's index in both services :beaming_face_with_smiling_eyes:
- Setup a sponsorship page and allow users and organisations who appreciate your project to help raise for its development (and add a badge in the process! :sunglasses:). Popular platforms are:
  - [`Liberapay`][wno3];
  - [`Open Collective`][wno4];
  - [`Ko-fi`][wno5];
  - Of course, you can also set any kind of gateway you wish, what works best for you and your project!

And here are a few articles which may help you:

- [Open Source Guides][wno6];
- [A handy guide to financial support for open source][wno7];
- [GitLab CI Documentation][lab2];
- [A Comprehensive Look at Testing in Software Development][wn22] is an article that lays out why testing is crucial for development success. Eric's blog is actually a great reference, covering topics ranging from the basics to advanced techniques and best practices;
- [Robust Exception Handling][wn23];
- [Why Your Mock Doesn't Work][wn24];
- [Managing TODOs in a codebase][wn25].

## :rocket: Features

### Development features

- Support for `Python 3.9` and higher;
- Provides minimal boilerplate code for a CLI with TUI application, using [`Typer`][app1] and [`Textual`][app2];
- Uses [`Poetry`][ft1] as the dependency manager and extends functionality with [`dynamic versioning`][ft2], [`virtual environment bundling`][ft3], dependency [`export`][ft4] and [`update resolution`][ft5]. See configuration in [`pyproject.toml`][ft6];
- Automatic code formatting with [`ruff`][fo1], with ready-to-use [`pre-commit`][fo2] hooks and several rules already selected for linting;
- Type checks with [`mypy`][ft7], security checks with [`safety`][ft8] and [`bandit`][ft9];
- Testing with [`pytest`][ft10] and [`behaviour-driven development`][bdd1] configuration for managing scenarios; more details in the [Behaviour-Driven Development][bdd2] section;
- Code quality integrations with [`Codacy`][ft11] via CI/CD;
- Predefined VS Code [`settings.json`][ft12] with quality-of-life configuration for editor, workbench, debugging and more;
- Ready-to-use [`.editorconfig`][ft13], [`.dockerignore`][docker1] and [`.gitignore`][ft14] files. You don't have to worry about those things.

### Deployment features

- Predefined CI/CD build workflow with [`GitLab CI`][lab3];
- Automatic package uploads to [`PyPI`][ft15] test and production repositories;
- Everything is already set up for security checks, codestyle checks, code formatting, testing, linting, docker builds etc with [`Invoke`][ft16]. More details in [Invoke Usage][ft17];
- [`Dockerfile`][docker2] for your package, with CI/CD workflows to publish your image to a container registry;
- Automatic [`Changelog entries`][lab4] updated via [GitLab API][lab5] and [template][lab8].

### Project management features

- Issue and Merge Request templates for easy integration with GitLab;
- Workflows to mark and close abandoned issues after a period of inactivity with GitLab [`Triage Policies`][lab9];
- [Gitmoji][bcv2] as the standard for commit titles.

### Open source community features

- Ready-to-use [Merge Request templates][ft18] and several [Issue templates][ft19];
- Files such as: `LICENCE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff` and `SECURITY.md` are generated automatically;
- **Loads** of predefined [badges][ft20] to make your project stand out, you can either keep them, remove as you wish or be welcome to add even more.

## Installation

```bash
pip install -U python-project
```

or install with `Poetry`:

```bash
poetry add python-project
```
Then you can run

```bash
python-project --help
```

or with `Poetry`:

```bash
poetry run python-project --help
```

### Invoke usage

[`invoke`][ft16] contains a lot of functions for faster development.

<details>
<summary>1. Download or remove Poetry</summary>
<p>

To download and install Poetry as a [standalone application][fs1] run:

```bash
invoke poetry-download
```

To uninstall

```bash
invoke poetry-remove
```

Alternatively, you can install it via your package manager (preferred) or any method provided by the [documentation][inv1].

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

Install requirements with

```bash
invoke install
```

And then add Poetry plugins to make development easier with

```bash
invoke poetry-plugins
```

Pre-commit hooks could be installed after `git init` via

```bash
invoke pre-commit-install
```

</p>
</details>

<details>
<summary>3. Codestyle</summary>
<p>

Automatic formatting uses `ruff`, and can be run with

```bash
invoke codestyle

# or use synonym
invoke format
```

For formatting checks only, without rewriting files:

```bash
invoke codestyle --check
```

Aside from the formatter, you can also use `ruff` to lint project files with several preconfigured rules defined in `pyproject.toml`:

```bash
invoke check-linter
```

</p>
</details>

<details>
<summary>4. Code security</summary>
<p>

```bash
invoke check-safety
```

This command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.

Update all dev libraries to the latest version using one command:

```bash
invoke update-dev-deps
```

</p>
</details>

<details>
<summary>5. Type checks</summary>
<p>

Run `mypy` static type checker with

```bash
invoke mypy
```

</p>
</details>

<details>
<summary>6. Tests</summary>
<p>

Run `pytest` with all essential parameters predefined with

```bash
invoke test
```

</p>
</details>

<details>
<summary>7. All code-related checks</summary>
<p>

Of course there is a command to ~~rule~~ run all linters in one:

```bash
invoke sweep
```

The same as:

```bash
invoke test check-linter codestyle mypy check-safety
```

</p>
</details>

<details>
<summary>8. Docker</summary>
<p>

Build your Docker image with the `latest` tag preconfigured with

```bash
invoke docker-build
```

Remove docker image with

```bash
invoke docker-remove
```

More information about Docker [here][docker3].

</p>
</details>

<details>
<summary>9. Cleanup</summary>
<p>

Delete pycache files:

```bash
invoke pycache-remove
```

Remove package build:

```bash
invoke build-remove
```

Delete .DS_STORE files:

```bash
invoke dsstore-remove
```

Remove .mypycache:

```bash
invoke mypycache-remove
```

Or to remove all above run:

```bash
invoke cleanup
```

</p>
</details>


# Behaviour-Driven Development

A `features` directory is placed under `tests`, with [`pytest-bdd`][bdd3] added as a dependency. You should create `.feature` files inside this folder to specify them and describe scenarios using the [Gherkin][bdd4] language:

```
# tests/features/divide.feature
Feature: Divide numbers
  Scenario: Full division
    When I ask the calculator to divide "21" by "7"
    Then the screen should return "3" as an integer

  Scenario: Division by zero
    When I ask the calculator to divide any number by "0"
    Then the screen should return an error message
```

You would then use `pytest-bdd` to wrap each scenario referred in the feature file as a step by step validation:

```py
from mypackage import divide
from pytest_bdd import scenario, when, then

@scenario("divide.feature", "Full Division")
def test_full_division():
    pass

@when("I ask the calculator to divide \"21\" by \"7\"")
def divide_21_7():
    calculation = divide(21, 7)

    return calculation

@then("The screen should return \"3\" as an integer")
def return_integer():
    assert calculation.display == "3"


@scenario("divide.feature", "Division by Zero")
def test_zero_division():
    pass

@when("I ask the calculator to divide any number by \"0\"")
def divide_by_zero():
    calculation = divide(15, 0)

    return calculation

@then("The screen should return an error message")
def return_integer():
    assert calculation.display == "Error"
```

Then you can simply use `pytest` as you normally would to run the test suite and check the results.

For more information on behaviour-driven development and more advanced cases, please check out the [Cucumber documentation][bdd5].


## :chart_with_upwards_trend: Releases

You can see the list of available releases on the [GitLab Releases][r1] page.

We follow [Semantic Versions][fs4] specification.

We use [`GitLab Changelog`][lab5] entries to track changes. You can categorise commits and Merge Requests made to this project using [git trailers][lab10] in your commit messages.

### List of trailers and corresponding categories

|            **Git trailer**            |    **Category in CHANGELOG**    |
| :-----------------------------------: | :-----------------------------: |
| `enhancement`, `feature`              | :rocket: Features               |
| `bug`, `refactoring`, `bugfix`, `fix` | :wrench: Fixes & Refactoring    |
| `build`, `ci`, `testing`              | :package: Build System & CI/CD  |
| `breaking`                            | :boom: Breaking Changes         |
| `documentation`                       | :memo: Documentation            |
| `dependencies`                        | :arrow_up: Dependencies updates |

## :shield: Licence

[![Licence][blic1]][blic2]

This project is licenced under the terms of the `MIT` licence. See [LICENCE][blic2] for more details.

## :page_with_curl: Citation

```bibtex
@misc{Python Project,
  author = {The Galactipy Contributors},
  title = {Awesome `python-project` is a Python cli/package created with https://gitlab.com/galactipy/galactipy},
  year = {2025},
  publisher = {GitLab},
  journal = {GitLab repository},
  howpublished = {\url{https://gitlab.com/galactipy/python-project}}
}
```

## Credits [![Expand your project structure from atoms of code to galactic dimensions.][bp6]][bp7]

This project was generated with [`galactipy`][bp7].

<!-- Anchors -->

[bp1]: https://img.shields.io/pypi/pyversions/python-project?style=for-the-badge
[bp2]: https://pypi.org/project/python-project/
[bp3]: https://img.shields.io/pypi/v/python-project?style=for-the-badge&logo=pypi&color=3775a9
[bp4]: https://gitlab.com/galactipy/python-project
[bp5]: https://gitlab.com/galactipy/python-project/-/releases
[bp6]: https://img.shields.io/badge/made%20with-galactipy%20%F0%9F%8C%8C-179287?style=for-the-badge&labelColor=193A3E
[bp7]: https://kutt.it/7fYqQl
[bp8]: https://img.shields.io/static/v1.svg?label=Contributions&message=Welcome&color=0059b3&style=for-the-badge
[bp9]: https://gitlab.com/galactipy/python-project/-/blob/master/CONTRIBUTING.md
[bp10]: https://gitlab.com/galactipy/python-project/-/issues
[bp11]: https://img.shields.io/badge/sembr-367DA9?style=for-the-badge&logo=read.cv&logoColor=white
[bp12]: https://sembr.org/
[bp13]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json&style=for-the-badge
[bp14]: https://python-poetry.org/
[bp15]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
[bp16]: https://gitlab.com/galactipy/python-project/-/blob/master/.pre-commit-config.yaml
[bp17]: https://img.shields.io/badge/security-bandit-yellow?style=for-the-badge
[bp18]: https://bandit.readthedocs.io/en/latest/
[bp19]: https://img.shields.io/badge/Editorconfig-E0EFEF?style=for-the-badge&logo=editorconfig&logoColor=000
[bp20]: https://gitlab.com/galactipy/python-project/-/blob/master/.editorconfig
[bp21]: https://img.shields.io/badge/semantic%20versions-4053D6?style=for-the-badge&logo=semver

[blic1]: https://img.shields.io/gitlab/license/galactipy/python-project?style=for-the-badge
[blic2]: https://gitlab.com/galactipy/python-project/-/blob/master/LICENCE

<!-- TODO Replace the `100` ID with your project's index at https://www.bestpractices.dev/en
[boss1]: https://img.shields.io/cii/level/100?style=for-the-badge&logo=linux-foundation&label=openssf%20best%20practices
[boss2]: https://www.bestpractices.dev/en/projects/100 -->
<!-- TODO Replace the `200` ID with your project's index at https://ossrank.com/
[boss3]: https://shields.io/endpoint?url=https://ossrank.com/shield/200&style=for-the-badge
[boss4]: https://ossrank.com/p/200 -->


<!-- TODO Replace the hash `d5402a91aa7b4234bd1c19b5e86a63be` with your project ID in the "Codacy Badge" section available at https://app.codacy.com/gl/galactipy/python-project/settings
[bcov1]: https://img.shields.io/codacy/grade/d5402a91aa7b4234bd1c19b5e86a63be?style=for-the-badge&logo=codacy
[bcov2]: https://app.codacy.com/gl/galactipy/python-project/dashboard
[bcov3]: https://img.shields.io/codacy/coverage/d5402a91aa7b4234bd1c19b5e86a63be?style=for-the-badge&logo=codacy
[bcov4]: https://app.codacy.com/gl/galactipy/python-project/coverage -->

[fs1]: https://github.com/python-poetry/install.python-poetry.org
[fs2]: https://python-poetry.org/docs/
[fs3]: https://python-poetry.org/docs/cli/#commands
[fs4]: https://semver.org/
[fs5]: https://git-scm.com/book/en/v2/Git-Basics-Tagging

[wn1]: https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree
[wn2]: https://github.com/tiangolo/typer
[wn3]: https://github.com/Textualize/textual
[wn4]: https://github.com/willmcgugan/rich
[wn5]: https://github.com/tqdm/tqdm
[wn6]: https://github.com/ijl/orjson
[wn7]: https://github.com/samuelcolvin/pydantic/
[wn8]: https://github.com/dry-python/returns
[wn9]: https://github.com/Delgan/loguru
[wn10]: https://github.com/gruns/icecream
[wn11]: https://github.com/facebookresearch/hydra
[wn12]: https://github.com/tiangolo/fastapi
[wn13]: https://shields.io/badges/static-badge
[wn14]: https://badges.pages.dev/
[wn15]: https://github.com/badges/awesome-badges
[wn16]: https://www.bestpractices.dev/en
[wn17]: https://ossrank.com/
[wn18]: https://coveralls.io/
[wn19]: https://about.codecov.io/
[wn20]: https://codeclimate.com/velocity/what-is-velocity
[wn21]: https://www.codacy.com/
[wn22]: https://pytest-with-eric.com/introduction/types-of-software-testing/
[wn23]: https://eli.thegreenplace.net/2008/08/21/robust-exception-handling/
[wn24]: https://nedbatchelder.com/blog/201908/why_your_mock_doesnt_work.html
[wn25]: https://medium.com/babylon-engineering/todo-find-a-title-for-the-article-fee79708ca15

[wno3]: https://liberapay.com/
[wno4]: https://opencollective.com/
[wno5]: https://ko-fi.com/
[wno6]: https://opensource.guide/
[wno7]: https://github.com/nayafia/lemonade-stand

[app1]: https://typer.tiangolo.com/

[app2]: https://textual.textualize.io/

[ft1]: https://python-poetry.org/
[ft2]: https://github.com/mtkennerly/poetry-dynamic-versioning
[ft3]: https://github.com/python-poetry/poetry-plugin-bundle
[ft4]: https://github.com/python-poetry/poetry-plugin-export
[ft5]: https://github.com/MousaZeidBaker/poetry-plugin-up
[ft6]: https://gitlab.com/galactipy/python-project/-/blob/master/pyproject.toml
[ft7]: https://mypy.readthedocs.io
[ft8]: https://docs.safetycli.com/safety-2/
[ft9]: https://bandit.readthedocs.io/en/latest/
[ft10]: https://docs.pytest.org/en/latest/
[ft11]: https://www.codacy.com/
[ft12]: https://gitlab.com/galactipy/python-project/-/blob/master/.vscode/settings.json
[ft13]: https://gitlab.com/galactipy/python-project/-/blob/master/.editorconfig
[ft14]: https://gitlab.com/galactipy/python-project/-/blob/master/.gitignore
[ft15]: https://pypi.org/
[ft16]: https://docs.pyinvoke.org/en/stable/
[ft17]: #invoke-usage
[ft18]: https://gitlab.com/galactipy/python-project/-/blob/master/.gitlab/merge_request_templates/default.md
[ft19]: https://gitlab.com/galactipy/python-project/-/tree/master/.gitlab/issue_templates
[ft20]: https://shields.io/

[inv1]: https://python-poetry.org/docs/#installation

[r1]: https://gitlab.com/galactipy/python-project/-/releases

[bscm1]: https://img.shields.io/badge/GitLab-330F63?style=for-the-badge&logo=gitlab&logoColor=white
[bscm2]: https://img.shields.io/gitlab/v/release/galactipy%2Fpython-project?style=for-the-badge&logo=semantic-release&color=FFCA28
[bscm3]: https://img.shields.io/gitlab/issues/open/galactipy%2Fpython-project?style=for-the-badge&color=fca326
[bscm4]: https://img.shields.io/gitlab/merge-requests/open/galactipy%2Fpython-project?style=for-the-badge&color=6fdac9
[bscm5]: https://gitlab.com/galactipy/python-project/-/merge_requests
[bscm6]: https://img.shields.io/gitlab/pipeline-status/galactipy%2Fpython-project?branch=master&style=for-the-badge&logo=gitlab&logoColor=white&label=master
[bscm7]: https://gitlab.com/galactipy/python-project/-/pipelines

[lab1]: https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html
[lab2]: https://docs.gitlab.com/ee/ci/
[lab3]: https://gitlab.com/galactipy/python-project/-/blob/master/.gitlab-ci.yml
[lab4]: https://gitlab.com/galactipy/python-project/-/blob/master/CHANGELOG.md
[lab5]: https://docs.gitlab.com/ee/user/project/changelogs.html
[lab6]: https://gitlab.com/explore/catalog/components/gitlab-triage
[lab7]: https://gitlab.com/galactipy/python-project/-/blob/master/.triage-policies.yml
[lab8]: https://gitlab.com/galactipy/python-project/-/blob/master/.gitlab/changelog_config.yml
[lab9]: https://gitlab.com/explore/catalog/components/gitlab-triage
[lab10]: https://docs.gitlab.com/ee/user/project/changelogs.html#add-a-trailer-to-a-git-commit

[bdocker1]: https://img.shields.io/gitlab/v/release/galactipy%2Fpython-project?style=for-the-badge&logo=linux-containers&logoColor=C5F4EC&label=image&color=C5F4EC
[bdocker2]: https://gitlab.com/galactipy/python-project/container_registry

[docker1]: https://gitlab.com/galactipy/python-project/-/blob/master/.dockerignore
[docker2]: https://gitlab.com/galactipy/python-project/-/blob/master/docker/Dockerfile
[docker3]: https://gitlab.com/galactipy/python-project/-/tree/master/docker

[bfo1]: https://img.shields.io/badge/code%20style-ruff-261230?style=for-the-badge&labelColor=grey
[bfo2]: https://docs.astral.sh
[bfo3]: https://img.shields.io/badge/imports-isort-1674b1?style=for-the-badge&labelColor=ef8336
[bfo4]: https://pycqa.github.io/isort/

[fo1]: https://black.readthedocs.io/en/stable/
[fo2]: https://pre-commit.com/

[bli1]: https://img.shields.io/badge/docstrings-numpydoc-4dabcf?style=for-the-badge&labelColor=4d77cf
[bli2]: https://numpydoc.readthedocs.io/en/latest/format.html

[bbbd1]: https://img.shields.io/badge/BDD-23D96C?style=for-the-badge&logo=cucumber&logoColor=white
[bbbd2]: https://cucumber.io/

[bdd1]: https://cucumber.io/
[bdd2]: #behaviour-driven-development
[bdd3]: https://pytest-bdd.readthedocs.io/en/latest/
[bdd4]: https://cucumber.io/docs/gherkin/reference
[bdd5]: https://cucumber.io/docs
[bcv1]: https://img.shields.io/badge/%F0%9F%98%9C_gitmoji-ffdd67?style=for-the-badge
[bcv2]: https://gitmoji.dev/
