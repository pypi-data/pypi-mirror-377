# Tobiko Cloud CLI

## Configuration

### Configuration Wizard

To use the built-in wizard to configure the CLI, run `tcloud project add`.
It will prompt you for the information required to configure a Tobiko Cloud project.
It will store the result of your inputs at `$HOME/.tcloud/tcloud.yml`.

### Manual

The configuration for the `tcloud` CLI tool should be stored either in the
`$HOME/.tcloud/tcloud.yml` file or in the `tcloud.yml` file located in the
project folder.

Below is an example of `tcloud.yml` configuration:
```yaml
projects:
    <Project name>:
        url: <The project URL>
        token: <The access token>
        gateway: <The name of the SQLMesh gateway to use with this project>
        extras: <Optional - Any extras that should be installed with sqlmesh-enterprise>
        pip_executable: <Optional - The path to the pip executable to use. Ex: `uv pip` or `pip3`. Must install packages to the python environment running the tcloud command>
default_project: <The name of a project to use by default>
```

Alternatively, the target project can be configured using the `TCLOUD_URL`,
`TCLOUD_TOKEN`, `TCLOUD_GATEWAY`, `TCLOUD_EXTRAS`, and `TCLOUD_PIP_EXECUTABLE`
environment variables.

The `token` field or `TCLOUD_TOKEN` environment variables are only needed if
you're sqlmesh environment is not setup for Single Sign On.

## Single Sign On
If you're tcloud environment is setup to require SSO than you should **NOT**
provide a `token` field in your `tcloud.yml` configuration. As long as a `token`
field is not provided the tcloud CLI tool should attempt to log you in when
running operations that require authentication.

The tcloud CLI tool has an `auth` command that can help you manage your
authentication. Please run `tcloud auth` to see the available commands and refer
to the following examples:

### Status
You can see what the status of your session with the `status` command:

``` shell
> tcloud auth status
Not currently authenticated
```

### Login

In order to initial the login process you can run the `login` command:

``` shell
> tcloud auth login
Logging into Tobiko Cloud

Opening your browser to the signin URL 🌐

If a browser doesn't open on your system please go to the following url:
<login_url>

This url has also been copied to your system clipboard 📋
```

At this point your system browser should open and allow you to log in. If you
are already logged in this might be a very quick process. When done you will be
prompted with a success message in your browser and a message telling you that
it's safe to close your browser window. Your terminal will then have the
following result:

``` shell
Success! ✅

Current Tobiko Cloud SSO session expires in 1439 minutes
```

The `status` command will now return the same information:

``` shell
> tcloud auth status
Current Tobiko Cloud SSO session expires in 1439 minutes
```

### Logout
In order to delete your session information you can use the `logout` command:

``` shell
> tcloud auth logout
Logged out of Tobiko Cloud

> tcloud auth status
Not currently authenticated
```

### Refresh
When your authentication session is close to expiring, any tcloud or sqlmesh
command that requires SSO will attempt to refresh your token. You can also
refresh your token manually with the `refresh` command.

```
> tcloud auth refresh
Refreshing your authentication token 🔄
```

### Force Login
By default the `login` command will just return information about your current
session if you are already logged in. In order to force a new login you can
either `logout` first or run with the `-f` flag:


``` shell
> tcloud auth status
Current Tobiko Cloud SSO session expires in 1439 minutes

> tcloud auth login
Current Tobiko Cloud SSO session expires in 1439 minutes

> tcloud auth login -f
Logging into Tobiko Cloud

Opening your browser to the signin URL 🌐

If a browser doesn't open on your system please go to the following url:
<login_url>

This url has also been copied to your system clipboard 📋

Success! ✅

Current Tobiko Cloud SSO session expires in 1439 minutes
```

## Service to Service

We support service to service use by using the OAuth client credentials flow
with clients created from your cloud instance. To use this flow just make sure
the `TCLOUD_CLIENT_ID` and `TCLOUD_CLIENT_SECRET` environment variables are set
with the proper values. All of the commands from the previous session work but
instead of opening a browser to log you in, the client will refresh it's token
automatically using the provided client information.

## Executing arbitrary commands

The `tcloud` CLI tool allows you to execute arbitrary shell commands while making sure that the SQLMesh Enterprise Python package is in sync with the version of your project deployment in Tobiko Cloud.

To execute an arbitrary command, use the `tcloud exec` command followed by the command you wish to execute. For example:

```
tcloud exec echo "Hello, world!"
```

The above commands checks the installed version of the SQLMesh Enterprise Python package and then executes the `echo` command with the given argument.

This command is particularly useful when running custom wrapper scripts built on top of the SQLMesh CLI or Python API, as it ensures they execute with a compatible version of the SQLMesh Enterprise Python package.


## Running self-hosted executors

The `tcloud` CLI tool allows you to run SQLMesh executor processes which can
perform cadence model evaluations and plan applications outside the Tobiko Cloud
environment.

To launch an executor process responsible for runs: `tcloud executor run`.

To launch an executor process responsible for plan applications: `tcloud
executor plan`.

Any number of executors, of either type, can be launched as needed. The actual
number should be determined by the specific requirements of a given project. For
instance, a project with numerous users frequently applying changes concurrently
may benefit from a higher number of `plan` executors.

The gateway / connection configuration can be provided using environment
variables as described in the
[documentation](https://sqlmesh.readthedocs.io/en/latest/guides/configuration/?h=environment+varia#overrides).
