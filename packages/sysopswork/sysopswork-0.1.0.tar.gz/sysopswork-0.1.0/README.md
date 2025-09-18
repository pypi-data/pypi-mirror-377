# SysOpsWork

**SysOpsWork** python package is used to simplify communication with [SysOpsWork](https://sysopswork.com) system.

## Installing SysOpsWork

SysOpsWork is available on PyPI. SysOpsWork python package is installed as part of a Dockerfile:

```console
RUN pip3 install sysopswork
```

The command might differ depending on the container image used.

SysOpsWork officially supports Python 3.9+.

## Importing SysOpsWork

At your python script, import sysopswork, with:

```python
import sysopswork
```

## Using SysOpsWork

Below are the functions that can be used with SysOpsWork module:

To get the value provided by user on template form input:

```python
input_value = sysopswork.getInputVal(input_id)
```

Replace `input_id` by the input ID used on template.

To get the value of a secret (the user running the script needs the right privileges for that):

```python
secret_value = sysopswork.getSecretVal(secret_name)
```

Replace `secret_name` by the respective secret name.
