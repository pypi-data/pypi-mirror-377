[![Gitlab CI](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/badges/main/pipeline.svg)](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/-/pipelines)
[![codecov](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/badges/main/coverage.svg)](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/odoo-openupgrade-wizard)
![PyPI - Downloads](https://img.shields.io/pypi/dm/odoo-openupgrade-wizard)
![GitLab last commit](https://img.shields.io/gitlab/last-commit/34780558)
![GitLab stars](https://img.shields.io/gitlab/stars/34780558?style=social)

# Odoo OpenUpgrade Wizard

**Odoo OpenUpgrade Wizard** is a powerful tool designed to help developers perform major
upgrades of Odoo Community Edition (formerly OpenERP).

Designed for complex migrations, Odoo OpenUpgrade Wizard integrates tightly with the
[OCA OpenUpgrade](https://github.com/oca/openupgrade) project to streamline and
automate the migration process. There is no need to download or install OCA OpenUpgrade
separately - Odoo OpenUpgrade Wizard handles the integration for you automatically!

Key features include:
* **Multi-version upgrades:** Migrate sequentially across several Odoo versions in one
  workflow.
* **Module installation control**: Install or uninstall modules as part of the migration
  workflow.
* **Automation hooks:** Execute custom SQL queries or Odoo shell scripts before and
  after each migration step.
* **Workload estimation:** Analyze and report on the migration effort and module
coverage.
* **Reproducible environments:** Automate Docker-based build and testing environments
  for each upgrade step.
* **Automatic integration with OCA OpenUpgrade:** Automatic cloning and integration
  with the powerful OCA OpenUpgrade project.

Odoo OpenUpgrade Wizard sets up a dedicated migration environment, fetching all
necessary code and dependencies. It provides helpers to run, test, and replay migration
steps until your upgrade is successful.

# Table of Contents

* [Quick Start Guide](#quick-start-guide)
* [Installation](#installation)
* [Usage](#usage)
    * [Command ``init``](#command-init)
    * [Command ``pull-submodule``](#command-pull-submodule)
    * [Command ``get-code``](#command-get-code)
    * [Command ``guess-requirement``](#command-guess-requirement)
    * [Command ``docker-build``](#command-docker-build)
    * [Command ``run``](#command-run)
    * [Command ``install-from-csv``](#command-install-from-csv)
    * [Command ``upgrade``](#command-upgrade)
    * [Command ``generate-module-analysis``](#command-generate-module-analysis)
    * [Command ``estimate-workload``](#command-estimate-workload)
    * [Command ``psql``](#command-psql)
    * [Command ``copydb``](#command-copydb)
    * [Command ``dropdb``](#command-dropdb)
    * [Command ``dumpdb``](#command-dumpdb)
    * [Command ``restoredb``](#command-restoredb)
    * [Command ``execute-script-python``](#command-execute-script-python)
    * [Command ``execute-script-sql``](#command-execute-script-sql)
* [Contributing](#project-roadmap--contributing)

<a name="quick-start-guide"/>

# Quick Start Guide

1. Install Odoo OpenUpgrade Wizard via pipx:
```shell
pipx install odoo-openupgrade-wizard
```

2. Initialize your environment:
```shell
oow init
```

3. Get the code and start using the tool:
```shell
oow get-code
oow docker-build
oow run
```
See below for complete command reference.

<a name="installation"/>

# Installation

**Prerequisites**

* **Operating System:** Supported on Debian-based Linux and macOS.
* **Docker:** Must be installed for running migration environments.
* **Python:** 3.9, 3.10, 3.11, and 3.12 are supported.
* For full feature support, ensure system-level build tools and libraries are present
(see `DEVELOP.md` for details).

**Install from PyPI**

The library is available on [PyPI](https://pypi.org/project/odoo-openupgrade-wizard/).

The easiest way to install Odoo OpenUpgrade Wizard is with
[pipx](https://pypa.github.io/pipx/):

```shell
pipx install odoo-openupgrade-wizard
```

Alternatively, use pip in a virtual environment:

```shell
python -m venv venv
source venv/bin/activate
pip install odoo-openupgrade-wizard
```

For development installation and advanced setup, see the ``DEVELOP.md`` file.

<a name="usage"/>

# Usage

Once installed, the CLI tool is available as either ``odoo-openupgrade-wizard`` or
``oow``.

**Tips**

* The term ``odoo-openupgrade-wizard`` can be replaced by ``oow``
in all the command lines below.

* All commands support --help for additional details, for example:
  * ``odoo-openupgrade-wizard --help`` or ``oow --help``
  * ``odoo-openupgrade-wizard init --help`` or ``oow init --help``

<a name="command-init"/>

## Command: ``init``

**Prerequisites:** Current working directory is your desired project directory
(see **Tips** below)

Initializes a new migration project. Creates the directory structure and configuration
files for your migration project inside the current directory, including per-version
environments, scripts, and settings.

You can provide all options directly as command-line arguments, or simply run
the ``init`` command without them and you will be interactively prompted for any
required information.

```shell
odoo-openupgrade-wizard init\
  --initial-version 11.0\
  --final-version 15.0\
  --project-name upg-customer-11-15\
  --extra-repository OCA/web,OCA/server-tools\
  --postgresql-version 12
```

**Parameters**

* ``--initial-version`` **(Required)** The current Odoo version that you are migrating
  from. Example: 11.0
* ``--final-version`` **(Required)** The desired final Odoo version that you are
  migrating to. This may be several versions greater than the ``--initial-version``.
  Example: 18.0
* ``--project-name`` **(Required)** A user-friendly name to help identify the Docker
  images. Must not contain spaces, special characters, or uppercase letters.
  Example: my-customer-16-18
* ``--extra-repository`` **(Required)** Comma-separated list of extra repositories to
  use in the Odoo environment.
  Example: OCA/web,OCA/server-tools,GRAP/grap-odoo-incubator
* ``--postgresql-version`` **(Required)** The version of PostgreSQL that will be used
  to create the PostgreSQL container. Example: 10, 16, etc.
  The version should be available in Docker hub (https://hub.docker.com/_/postgres).
  Avoid the 'latest' version if you want a deterministic installation.
  **Important:** If your current production server uses PostgreSQL version A and your
  future production server will use PostgreSQL version B, you should select here a
  version X, with A <= X <= B.

**Example: Example command to initialize a project to upgrade from Odoo 10.0 to Odoo 12.0:**

```shell
odoo-openupgrade-wizard init\
  --initial-version 10.0\
  --final-version 12.0\
  --project-name my-customer-10-12\
  --extra-repository OCA/web,OCA/server-tools\
  --postgresql-version 10
```
This will generate the following structure (some directories/files will only appear
after subsequent oow commands, such as ``run``, ``generate-module-analysis``, etc.)
but are provided here for context and clarity:

```
config.yml
modules.csv
filestore/
log/
    2022_03_25__23_12_41__init.log
    ...
postgres_data/
scripts/
    step_01__regular__10.0/
        pre-migration.sql
        post-migration.py
    step_02__openupgrade__11.0/
        ...
    step_03__openupgrade__12.0/
        ...
    step_04__regular__12.0/
        ...
src/
    env_10.0/
        addons_debian_requirements.txt
        addons_python_requirements.txt
        extra_debian_requirements.txt
        extra_python_requirements.txt
        Dockerfile
        odoo.conf
        repos.yml
        src/
    env_11.0/
        ...
    env_12.0/
        ...
```

**Key Files and Directories**

* ``config.yml`` Main project configuration. Contains the options selected with the
  `init` command plus other user-configurable settings. For example, country_code (used
  by the ``install-from-csv`` command), and workload_settings (used by the
  ``estimate-workload`` command).

* ``modules.csv`` (optional) Lists the modules installed on the production system to be
  upgraded. The first column of this file should contain the technical name of the
  module.

* ``filestore/`` Odoo filestore(s) for each of the Odoo databases.  This directory
  is not created by the ``oow init`` command, but instead is generated by any of the
  commands that create an Odoo database (e.g. ``oow run``, ``oow install-from-csv``,
  etc.)

* ``log/`` Contains all logs generated by ``odoo-openupgrade-wizard`` during migration
  steps and the logs of the Odoo instance.

* ``postgres_data/`` This directory is not created by the ``oow init`` command, but
  is just a suggested location to store your database & filestore backups. This ensures
  that the PostgreSQL Docker container has access to the files when required
  (e.g. during commands such as ``oow restoredb``).

* ``scripts/`` Contains a subdirectory for each migration step
  (e.g. ``step_01__regular__10.0``). In each ``step_xx`` subdirectory:
  - ``pre-migration.sql`` Extra SQL queries to execute before beginning the step.
  - ``post-migration.py`` Extra python commands to execute after the completion of the
    step. Script will be executed with the ``odoo shell`` command. All the ORM is
    available via the ``env`` variable.

* ``src/`` Contains a subdirectory for each Odoo version in the project
  (e.g. ``env_10.0``) with source code and requirements for each Odoo version. In
  each environment directory:

    - ``addons_debian_requirements.txt`` Lists Debian (system-level) packages that are
      required by the Odoo addons (modules) specified in your migration. These packages
      are automatically installed in the Docker environment to ensure your Odoo
      instance has all necessary system dependencies. This file is autopopulated by
      the ``oow guess-requirement`` command based on the addons listed in the
      ``modules.csv`` file.

    - ``addons_python_requirements.txt`` Similar to ``addons_debian_requirements.txt``
       but for Python packages (autopopulated by the ``oow guess-requirement`` command).

    - ``extra_debian_requirements.txt`` Allows you to specify any additional Debian
      (system-level) packages needed beyond those detected for your modules. Use this
      file to manually add system dependencies that are unique to your customizations
      or specific project needs but were not automatically detected by the
      ``oow guess-requirement`` command.

    - ``extra_python_requirements.txt`` Lets you list additional Python packages
      required by your environment, beyond what is automatically detected for your
      modules by the ``oow guess-requirement`` command. The syntax should respect
      the ``pip install -r`` command
      (see: https://pip.pypa.io/en/stable/reference/requirements-file-format/).

    - ``Dockerfile`` Used to build a custom Docker image tailored for each
      step of the migration. The Dockerfile pulls a compatible Debian base image,
      installs required system packages and Python dependencies (from the generated
      requirements files), and applies any extra configuration.

    - ``odoo.conf`` Add any non-standard configuration required for your custom modules.
      This file can be left empty. Only list non-standard or special options not
      included in the standard parameters. The Odoo OpenUpgrade Wizard code
      automatically generates standard parameters such as addons paths, database
      connection details, HTTP/XML ports, etc.

    - ``repos.yml`` Defines which Git repositories (and which branches or pull requests)
      should be cloned and included in the environment for a specific Odoo version
      during your migration. The syntax should respect the ``gitaggregate`` command
      (see: https://pypi.org/project/git-aggregator/).
      This file is autopopulated based on the repositories included in the ``oow init``
      command, though you can update them with your custom settings (custom branches,
      extra PRs, git shallow options, etc.)

**Note**

- In your ``repos.yml`` file, preserve the ``openupgrade`` repository to have all the
  features of this library available.
- In your ``repos.yml`` file, the Odoo project should be in ``./src/odoo``
  and the openupgrade project should be in the ``./src/openupgrade/`` directory.

**Tips**

- A good habit is to always include ``--extra-repository OCA/server-tools``
  to ensure that the features this repo provides are available (required for running
  some Odoo OpenUpgrade Wizard commands such as ``oow generate-module-analysis``).
- You can use the default generated files if you have a basic Odoo instance without
  custom code, extra repositories, or dependencies, or you could edit the autogenerated
  files as needed for your specific migration scenario. For example:
  - In the ``config.yml`` file's 'regular' steps (i.e., first and last steps), you can
    change the default ``update: True`` to ``update: False`` to prevent the system from
    executing a time-consuming 'update=all' during the upgrade. In that case, only SQL
    queries and python scripts will be executed during this step.
  - In the ``config.yml`` file's ``odoo_default_company`` setting, you could change the
    ``country_code`` from the default 'FR' to your desired setting.

- This command builds the project scaffold inside the current directory. Therefore,
before running this command, create your project directory and `cd` to it:

```shell
mkdir my-oow-upgrade-project
cd my-oow-upgrade-project
oow init
```

<a name="command-pull-submodule"/>

## Command: ``pull-submodule``

**Prerequisites:** init + being in a git repository (if not, you can simply run ``git init``)

Optionally syncs a remote ``repos.yml`` file into your local migration project instead of
relying on providing an --extra-repository list to the ``oow init`` command or manually
copying/pasting from an already-existing ``repos.yml`` file.

To use a ``repos.yml`` file from your GitHub or GitLab repository, add the repository
configuration in the ``config.yml`` file for each Odoo version:

```yaml
odoo_version_settings:
  12.0:
      repo_url: url_of_the_repo_that_contains_a_repos_yml_file
      repo_branch: 12.0
      repo_file_path: repos.yml
```

Then run:

```shell
odoo-openupgrade-wizard pull-submodule
```
**Tips**

- Remember to always include the ``OCA/server-tools`` repo in your repos.yml file
  to ensure that the features this repo provides are available (required for running
  some Odoo OpenUpgrade Wizard commands such as ``oow generate-module-analysis``).

<a name="command-get-code"/>

## Command: ``get-code``

**Prerequisites:** init

Downloads all required Odoo source code and dependencies for each version defined in
your migration (uses the ``gitaggregate`` tools internally).

```shell
odoo-openupgrade-wizard get-code
```

The required repositories are defined in the ``repos.yml`` file of each environment
directory (or in the ``repo_submodule`` directory if you used the ``pull-submodule``
feature.)

**Note**

* This step could take a long time!

**Optional Arguments**

You can limit code updates to specific versions using the --versions parameter.

```shell
odoo-openupgrade-wizard get-code --versions 10.0,11.0
```

<a name="command-guess-requirement"/>

## Command: ``guess-requirement``

**Prerequisites:** init + get-code

Analyzes the list of modules defined in your ``modules.csv`` file to generate the
required Python and Debian package dependencies per environment.

```shell
odoo-openupgrade-wizard guess-requirement
```

For each module and each version, this command tries to parse the
corresponding ``__manifest__.py`` file (and, if present, the ``setup.py``
file). It then appends any discovered requirements to the appropriate
``addons_debian_requirements.txt`` and
``addons_python_requirements.txt`` files present in each env directory.

For example, here is the content of the ``addons_python_requirements.txt`` file
when ``barcodes_generator_abstract`` and ``l10n_fr_siret`` are listed in the
``modules.csv`` file (for v16).

```
# Required by the module(s): barcodes_generator_abstract
python-barcode

# Required by the module(s): l10n_fr_siret
python-stdnum>=1.18
```

<a name="command-docker-build"/>

## Command: ``docker-build``

**Prerequisites:** init + get-code

Builds Docker images for each Odoo version/environment in your migration pipeline.

```shell
odoo-openupgrade-wizard docker-build
```

After the command has finished, the following command should show a Docker image per
version:

```shell
docker images --filter "reference=odoo-openupgrade-wizard-*"
```
```
REPOSITORY                                                 TAG       IMAGE ID       CREATED       SIZE
odoo-openupgrade-wizard-image---my-customer-10-12---12.0   latest    ef664c366208   2 weeks ago   1.39GB
odoo-openupgrade-wizard-image---my-customer-10-12---11.0   latest    24e283fe4ae4   2 weeks ago   1.16GB
odoo-openupgrade-wizard-image---my-customer-10-12---10.0   latest    9d94dce2bd4e   2 weeks ago   924MB
```

**Note**

* This step could also take a long time!

**Optional Arguments**

You can limit image builds to specific versions using the --versions parameter.

```shell
odoo-openupgrade-wizard docker-build --versions 10.0,12.0
```

<a name="command-run"/>

## Command: ``run``

**Prerequisites:** init + get-code + docker-build

Launches an Odoo instance for a specific migration step.

```shell
odoo-openupgrade-wizard run\
    --step 1\
    --database mydb
```

The database will be created if it doesn't already exist.

Unless the ``stop-after-init`` flag is used, the Odoo instance will be available
on your host at the following URL: http://localhost:9069
(port depends on the ``host_odoo_xmlrpc_port`` setting in your ``config.yml`` file).

**Optional Arguments**

* You can install modules using the --init-modules parameter
(e.g. ``--init-modules base,purchase,sale``).

* You can add the ``stop-after-init`` flag to turn off the process at the end
  of the installation.

<a name="command-install-from-csv"/>

## Command: ``install-from-csv``

**Prerequisites:** init + get-code + docker-build

Installs all modules listed in the ``modules.csv`` file into the specified database.

```shell
odoo-openupgrade-wizard install-from-csv\
    --database mydb
```

The database will be created if it doesn't exist.

To generate a proper ``modules.csv`` file, the following query can be used:
```shell
psql -c "copy (select name, shortdesc from ir_module_module where state = 'installed' order by 1) to stdout csv" coopiteasy
```

<a name="command-upgrade"/>

## Command: ``upgrade``

**Prerequisites:** init + get-code + docker-build

Performs the full database migration across all defined steps.

```shell
odoo-openupgrade-wizard upgrade\
    --database mydb
```

For each step, this will:

1. Run ``pre-migration.sql`` scripts.
2. Apply "update all" (in an upgrade or update context).
3. Run ``post-migration.py`` scripts via XML-RPC/Odoo shell (via ``odoorpc``).

**Optional Arguments**

* You can add ``--first-step 2`` to start at the second step.

* You can add ``--last-step 3`` to end at the third step.

<a name="command-generate-module-analysis"/>

## Command: ``generate-module-analysis``

**Prerequisites:** init + get-code + docker-build + OCA/server-tools in repos.yml

Performs an analysis between the target version (represented by the step parameter)
and the previous version to indicate how the data model and module data have
changed between the two versions (uses the OCA/server-tools ``upgrade_analysis`` tool
internally).

```shell
odoo-openupgrade-wizard generate-module-analysis\
    --database mydb\
    --step 2\
    --modules custom_module_name1,custom_module_name2
```

This tool will generate analysis files (e.g. ``upgrade_analysis.txt``,
``noupdate_changes.xml``, etc.) depending on the following:
- In the case of core Odoo modules, the analysis files will be located in the project's
  ``src/env_xx.0/src/openupgrade/openupgrade_scripts/scripts/{module_name}/{module_version}``
  directory.
- In the case of third-party modules (e.g. OCA or your own custom modules), the
  analysis files will be located  modules' ``migrations/{module_version}`` directory
  (e.g.
  ``src/env_xx.0/src/{organization}/{repo}/{module_name}/migrations/{module_version}``).

**Notes**

This command requires the ``upgrade_analysis`` module from the ``OCA/server-tools`` repository.
Be sure this repo is included in your ``repos.yml`` and pulled via ``oow get-code``.

**Tips**

- You can also use this function to analyze differences for custom & OCA modules
  between several versions (e.g. in case of refactoring).
- If you get an error running this command, you may not have included
  ``--extra-repository OCA/server-tools`` in your ``oow init`` command (and thus the
  repo is not listed in your ``repos.yml`` file).

<a name="command-estimate-workload"/>

## Command: ``estimate-workload``

**Prerequisites:** init + get-code

Generates an HTML report (``analysis.html``) with all the information regarding
the work to do for the migration for the modules listed in ``modules.csv`` (or passed
via the command-line arguments).

```shell
odoo-openupgrade-wizard estimate-workload
```

Features:
- Checks that the modules are present in each version (by managing the
  renaming or merging of modules)
- Checks that the analysis and migration have been done for the official
  modules present in odoo/odoo)

**Optional Arguments**

You can override the modules in ``modules.csv`` by passing a comma-separated list
using the --extra-modules parameter:

```shell
odoo-openupgrade-wizard estimate-workload --extra-modules account,product,base
```

<a name="command-psql"/>

## Command: ``psql``

**Prerequisites:** init + get-code + docker-build

Runs arbitrary SQL commands against the target database.

```shell
odoo-openupgrade-wizard psql\
    --database mydb\
    --command "SELECT count(*) FROM res_partner;"
```

Ensure that the ``command`` parameter contains a string with a valid psql statement
(including the statement terminator ";") or meta-command (e.g. \l, \dt).

**Optional Arguments**

**Database:** If no ``database`` is provided, the default ``postgres`` database can
be used by pressing Enter when prompted. For example:

```shell
odoo-openupgrade-wizard psql --command "\l"
```
You will be prompted to use the default database (i.e. [posgres]). Simply press Enter.

Result:
```
                              List of databases
    Name    | Owner | Encoding |  Collate   |   Ctype    | Access privileges
------------+-------+----------+------------+------------+-------------------
 postgres   | odoo  | UTF8     | en_US.utf8 | en_US.utf8 |
 template0  | odoo  | UTF8     | en_US.utf8 | en_US.utf8 | =c/odoo          +
            |       |          |            |            | odoo=CTc/odoo
 template1  | odoo  | UTF8     | en_US.utf8 | en_US.utf8 | =c/odoo          +
            |       |          |            |            | odoo=CTc/odoo
 test_psql  | odoo  | UTF8     | en_US.utf8 | en_US.utf8 |

```

**--pager/--no-pager:** To allow scrolling through long results, the "pager" option
is enabled by default via the click function ``echo_via_pager``
(see https://click.palletsprojects.com/en/8.1.x/utils/#pager-support).
Disable the pager feature by passing ``--no-pager``.

**Extra psql arguments:** You can pass extra psql arguments inline. All remaining
text after the known options are collected and passed unprocessed (i.e., they won’t
be parsed or validated by Click). These arguments are then appended directly to the
psql command line run inside the Docker container.

```shell
odoo-openupgrade-wizard psql\
    --database test_psql\
    --command "select id, name from res_partner where name ilike '%admin%';"
    -H
```
Result:
```html
<table border="1">
  <tr>
    <th align="center">id</th>
    <th align="center">name</th>
  </tr>
  <tr valign="top">
    <td align="right">3</td>
    <td align="left">Administrator</td>
  </tr>
</table>
<p>(1 row)<br />
</p>
```

For the complete list of extra psql argument options, see: https://www.postgresql.org/docs/current/app-psql.html

<a name="command-copydb"/>

## Command: ``copydb``

**Prerequisites:** init + get-code + docker-build

Creates an Odoo database (including filestore) by copying an existing one.

```shell
odoo-openupgrade-wizard copydb\
    --source my_current_db\
    --dest my_new_db
```

This script copies using postgres' CREATEDB WITH TEMPLATE. It also copies
the filestore.

<a name="command-dropdb"/>

## Command: ``dropdb``

**Prerequisites:** init + get-code + docker-build

Deletes an Odoo database and its filestore.

```shell
odoo-openupgrade-wizard dropdb\
    --database mydb
```

An exception will occur if the database does not exist.

<a name="command-dumpdb"/>

## Command: ``dumpdb``

Backs up a database and filestore, with options for output format.

**Prerequisites:** init + get-code + docker-build

```shell
odoo-openupgrade-wizard dumpdb\
    --database mydb\
    --database-path ./postgres_data\
    --filestore-path /path/to/myproject/postgres_data
```

Dumps the database mydb to ``--database-path`` and exports the filestore
related to mydb into ``--filestore-path``.

*WARNING*: The PostgreSQL Docker container must have access to the directories in the
``--database-path`` and ``--filestore-path`` parameters, therefore they must be inside
the project directory (as initialized by ``oow init``) using either an absolute path
or path relative to the project directory.

To choose the format of the backup files, see `--database-format` and
`--filestore-format` in Optional Arguments below.

**Optional Arguments**

* To choose the database format use `--database-format`. Format can be
  one of the following (for more information on formats, see:
  https://www.postgresql.org/docs/current/app-pgdump.html):
  - `p` for plain sql text
  - `c` (default format) for custom compressed backup of `pg_dump`
  - `d` for directory structure
  - `t` for a tar version of the directory structure

* To choose the filestore format use `--filestore-format`. Format can be
  one of the following:
  - `d` copy of the directory structure
  - `t` tar version of the directory structure (not compressed)
  - `tgz` (default format) tar version of the directory structure compressed with gzip

* By default, if the database file or filestore already exists, the
  command will fail, preserving the existing dump. If you need to
  overwrite the existing files, the `--force` option can be used.

<a name="command-restoredb"/>

## Command: ``restoredb``

Restores an Odoo database and its associated filestore from a previously created
backup. This command complements the dumpdb command and is useful when preparing
a fresh migration environment or recovering a snapshot.

**Prerequisites:** init + get-code + docker-build

```shell
odoo-openupgrade-wizard restoredb\
    --database mydb\
    --database-path ./postgres_data/db_backup\
    --database-format d\
    --filestore-path /path/to/myproject/postgres_data/filestore_backup
    --filestore-format d
```

**Parameters**

* ``--database`` **(Required)** Name of the database to restore. If it doesn’t exist,
  it will be created.
* ``--database-path`` **(Required)** Path to the database backup file or directory
  (must be inside your project path).
* ``--database-format`` Format of the database backup. One of: c (custom),
  d (directory), t (tar), p (plain SQL).
* ``--filestore-path`` **(Required)** Path to the filestore archive or directory.
* ``--filestore-format`` Format of the filestore backup. One of: d (directory),
  t (tar), tgz (gzipped tar).

*WARNING*: The PostgreSQL Docker container must have access to the directories in the
``--database-path`` and ``--filestore-path`` parameters, therefore they must be inside
the project directory (as initialized by ``oow init``) using either an absolute path
or path relative to the project directory.

**Supported Database Formats**

* `c` (default format) Custom format created by pg_dump -Fc (default format of oow dumpdb)
* `d` Directory format (pg_dump -Fd)
* `t` Tar format (pg_dump -Ft)
* `p` Plain SQL (pg_dump without -F)

**Supported Filestore Formats**

* `d` A regular uncompressed directory
* `t` A tar archive
* `tgz` (default format) A tar archive compressed with gzip

**Example: Restoring a custom dump with gzipped filestore:**

```shell
odoo-openupgrade-wizard restoredb\
  --database myproject_v14\
  --database-path my_project/backups/db/myproject_v14.dump\
  --database-format c\
  --filestore-path my_project/backups/filestore/myproject_v14.tgz\
  --filestore-format tgz
```

This command:
1. Creates (or recreates) the myproject_v14 database.
2. Restores its contents from the compressed .dump file.
3. Restores its filestore from a .tgz archive into the filestore/filestore/myproject_v14/
   directory inside your migration environment.

<a name="command-execute-script-python"/>

## Command: ``execute-script-python``

Executes one or more custom Python scripts in the context of a specific migration
step, using the Odoo shell (with full ORM access). This command allows you to manually
run Python logic outside of the default post-migration.py file for a given step.

**Prerequisites:** init + get-code + docker-build

```shell
odoo-openupgrade-wizard execute-script-python\
  --database mydb\
  --step 2\
  --script-file-path ./scripts/custom/my_script1.py,/path/to/myproject/scripts/custom/my_script2.py
```
Or:
```shell
odoo-openupgrade-wizard execute-script-python\
  --database mydb\
  --step 2\
  --script-file-path ./scripts/custom/my_script1.py\
  --script-file-path /path/to/myproject/scripts/custom/my_script2.py
```

**Parameters**

* ``--database`` **(Required)** Name of the database to operate on.
* ``--step`` **(Required)** The migration step (e.g. 1, 2, etc.), used to identify
  the environment.
* ``--script-file-path`` **(Optional, repeatable)** One or more paths to Python
  files within the project directory structure that you wish to execute. Each file
  will be run in the order listed. Overrides the default
  post-migration.py file in the step directory. The Docker container must have access
  to the directory/files, therefore the ``--script-file-path`` must be
  inside the project directory (as initialized by ``oow init``) using either an
  absolute path or path relative to the project directory.

**What It Does**

* Supplements the default post-migration.py logic.
* Executes each specified script within the Dockerized Odoo shell for the given
  migration step.
* You have full access to the Odoo environment (env object) inside each script, just
  like in odoo shell.

**Use Cases**

* Run custom ORM-based data transformations outside the full migration process.
* Test individual migration scripts before placing them into the step directory.
* Apply hotfixes without modifying the default post-migration.py.

**Script Example (fix_data.py)**

```python
# This will execute inside the Odoo shell context with 'env' available
partners = env["res.partner"].search([("customer_rank", ">", 0)])
for partner in partners:
    partner.comment = "Migrated customer"
```

**Notes**

* If multiple --script-file-path options are provided, they will be executed in
  the order given.
* All script paths must be located within the project directory structure initialized
  by ``oow init``. This is necessary so Docker has access to the files.
* This command is useful for debugging or running ad-hoc scripts, especially before
  committing them to the official step directory.

**Tips**
Store your custom Python scripts in a subdirectory under the standard ``scripts/``
directory for improved organization and version control (e.g. ``scripts/custom``,
``scripts/debug``, etc.)

**Example: Run a specific script manually**

```shell
odoo-openupgrade-wizard execute-script-python\
  --database my_database\
  --step 3\
  --script-file-path scripts/custom/fix_project.py
```

**Example: Using absolute and relative paths to the `my-oow-project`:**
```shell
odoo-openupgrade-wizard execute-script-python\
  --script-file-path /home/myhome/my-oow-project/scripts/custom/script1.py\
  --script-file-path scripts/custom/script2.py
```

**Example: Executing all scripts within a directory (the scripts will be run
alphabetically):**
```shell
odoo-openupgrade-wizard execute-script-python\
  --script-file-path scripts/custom/*.py
```

<a name="command-execute-script-sql"/>

## Command: ``execute-script-sql``

Executes one or more custom SQL scripts against the specified database using the
PostgreSQL Docker container. This command allows you to manually run SQL scripts,
allowing you to test or apply SQL changes in the context of a specific migration
step — outside the automatic oow upgrade process.

**Prerequisites:** init + get-code + docker-build

```shell
odoo-openupgrade-wizard execute-script-sql\
  --database mydb\
  --step 2\
  --script-file-path ./scripts/custom/my_script1.sql,/path/to/myproject/scripts/custom/my_script2.sql
```
Or:
```shell
odoo-openupgrade-wizard execute-script-sql\
  --database mydb\
  --step 2\
  --script-file-path ./scripts/custom/my_script1.sql\
  --script-file-path /path/to/myproject/scripts/custom/my_script2.sql
```

**Parameters**

* ``--database`` **(Required)** Name of the database to operate on.
* ``--step`` **(Required)** The migration step (e.g. 1, 2, etc.), used to identify
  the environment.
* ``--script-file-path`` **(Optional, repeatable)** One or more paths to .sql script
  files within the project directory structure that you wish to execute. Each file
  will be run in the order listed. Overrides the default
  pre-migration.sql file in the step directory. The Docker container must have access
  to the directory/files, therefore the ``--script-file-path`` must be
  inside the project directory (as initialized by ``oow init``) using either an
  absolute path or path relative to the project directory.

**What It Does**

* Runs one or more SQL files.
* If no --script-file-path is provided, it looks for all .sql files in the current
  step’s script directory (e.g. scripts/step_02__openupgrade__17.0/) and runs them
  in sorted order.
* Executes scripts using psql inside the Dockerized PostgreSQL container.

**Use Cases**

* Clean up or transform data before upgrading modules.
* Add or drop constraints, indexes, or columns before the ORM makes structural changes.
* Debug or experiment with SQL commands outside the full migration process.

**Notes**

* If multiple --script-file-path options are provided, they will be executed in
  the order given.
* All script paths must be located within the project directory structure initialized
  by ``oow init``. This is necessary so Docker has access to the files.
* This command is useful for debugging or running ad-hoc scripts, especially before
  committing them to the official step directory.
* Each SQL script is executed directly in the Postgres container using the
  psql CLI with full database access.

**Tips**
Store your custom SQL scripts in a subdirectory under the standard ``scripts/``
directory for improved organization and version control (e.g. ``scripts/custom``,
``scripts/debug``, etc.)

**Example: Run all .sql scripts in the step directory (sorted alphabetically)**

```shell
odoo-openupgrade-wizard execute-script-sql\
  --database my_database\
  --step 1
```

**Example: Run a specific script manually**

```shell
odoo-openupgrade-wizard execute-script-sql\
  --database my_database\
  --step 3\
  --script-file-path scripts/custom/fix_currency.sql
```

**Example: Using absolute and relative paths to the `my-oow-project`:**
```shell
odoo-openupgrade-wizard execute-script-sql\
  --script-file-path /home/myhome/my-oow-project/scripts/custom/script1.sql\
  --script-file-path scripts/custom/script2.sql
```

**Example: Executing all scripts within a directory (the scripts will be run
alphabetically):**
```shell
odoo-openupgrade-wizard execute-script-sql\
  --script-file-path scripts/custom/*.sql
```

<a name="project-roadmap--contributing"/>

# Project Roadmap & Contributing

We welcome your contributions!

* Please see `DEVELOP.md` for development setup, coding guidelines, and instructions
  on how to submit merge requests.
* Current limitations, known issues, and future features are tracked in the project's
  GitLab Issues: https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/-/issues
* The full list of contributors is available in `CONTRIBUTORS.md`.

_For additional details, troubleshooting, or to report issues, please visit our
[GitLab repository](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard)
or open a ticket._
