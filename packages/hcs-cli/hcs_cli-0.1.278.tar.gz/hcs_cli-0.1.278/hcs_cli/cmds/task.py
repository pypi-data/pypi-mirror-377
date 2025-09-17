"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import CtxpException, recent

from hcs_cli.service import task


@click.group(name="task")
def task_cmd_group():
    """Task management commands."""
    pass


@task_cmd_group.command("namespaces")
def list_namespaces(**kwargs):
    """List namespaces"""
    return task.namespaces()


@task_cmd_group.command()
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
@click.option("--reset", "-r", is_flag=True, default=False, help="If specified, reset the recent task.")
def use(namespace: str, group: str, smart_path: str, reset: bool, **kwargs):
    """Use a specific namespace, group, and/or task."""
    if reset:
        if namespace or group or smart_path:
            return "--reset can not be used with other parameteres.", 1
        recent.unset("task.namespace")
        recent.unset("task.group")
        recent.unset("task.key")
        return

    if namespace:
        recent.set("task.namespace", namespace)
        recent.unset("task.group")
        recent.unset("task.key")
    if group:
        recent.set("task.group", group)
        recent.unset("task.key")
    if smart_path:
        namespace, group, key = _parse_task_param(namespace, group, smart_path)

    namespace = recent.get("task.namespace")
    group = recent.get("task.group")
    key = recent.get("task.key")
    return f"{namespace}/{group}/{key}"


@task_cmd_group.command(name="list")
@click.option("--namespace", "-n", type=str, required=False, help="Filter tasks by namespace.")
@click.option("--group", "-g", type=str, required=False, help="Filter tasks by group.")
@click.option("--worker", "-w", type=str, required=False, help="Filter tasks by worker.")
@click.option("--type", "-t", type=str, required=False, help="Filter tasks by type.")
@click.option("--resource", "-r", type=str, required=False, help="Filter tasks by resource ID.")
@click.option("--queue", "-q", type=str, required=False, help="Filter tasks by queue ID.")
@click.option("--parent", "-p", type=str, required=False, help="Filter tasks by parent task ID.")
@click.option(
    "--meta",
    "-m",
    type=str,
    required=False,
    multiple=True,
    help="key-value pair to filter tasks by metadata. E.g. --meta key1=value1 --meta key2=value2",
)
@click.option(
    "--input",
    "-i",
    type=str,
    required=False,
    multiple=True,
    help="key-value pair to filter tasks by input. E.g. --input key1=value1 --input key2=value2",
)
@cli.limit
@cli.search
def list_tasks(
    namespace: str,
    group: str,
    worker: str,
    type: str,
    resource: str,
    queue: str,
    parent: str,
    meta: list[str],
    input: list[str],
    **kwargs,
):
    """List tasks."""
    if namespace:
        recent.set("task.namespace", namespace)
    else:
        namespace = recent.get("task.namespace")
        if not namespace:
            return "Missing recent namespace. Specify '--namespace'.", 1

    def _append_search(part: str):
        search = kwargs.get("search")
        if search:
            kwargs["search"] = f"{search} AND {part}"
        else:
            kwargs["search"] = part

    if group:
        recent.set("task.group", group)
        _append_search(f"group $eq {group}")
    if worker:
        _append_search(f"worker $eq {worker}")
    if type:
        _append_search(f"type $eq {type}")
    if resource:
        _append_search(f"resourceId $eq {resource}")
    if queue:
        _append_search(f"queueId $eq {queue}")
    if parent:
        _append_search(f"parentId $eq {parent}")
    if meta:
        for m in meta:
            k, v = m.split("=")
            _append_search(f"meta.{k} $eq {v}")
    if input:
        for i in input:
            k, v = i.split("=")
            _append_search(f"input.{k} $eq {v}")

    ret = task.query(namespace, **kwargs)
    if ret and len(ret) == 1:
        first = ret[0]
        recent.set("task.key", first["key"])
        recent.set("task.group", first["group"])
    return ret


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
def get(org: str, namespace: str, group: str, smart_path: str, **kwargs):
    """Get a task. E.g. 'task get [[<namespace>/]<group>/]<key>'."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    return task.get(org_id, namespace, group, key, **kwargs)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@click.option("--execution-id", "-e", type=str, required=False)
@click.option("--exclusive-id", "-x", type=str, required=False)
@cli.confirm
def delete(org: str, namespace: str, group: str, smart_path: str, execution_id: str, exclusive_id: str, confirm: bool, **kwargs):
    """Delete a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)
    print("start to delete")

    if not confirm:
        if not ret:
            click.confirm(f"Delete task {namespace}/{group}/{key}?", abort=True)
        else:
            click.confirm(f"Delete task {namespace}/{group}/{key}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.delete(org_id, namespace, group, key, execution_id, exclusive_id)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
@click.option("--last", is_flag=True, default=False, help="If specified, return only the last log instead of all logs.")
@cli.search
def logs(org: str, namespace: str, group: str, smart_path: str, last: bool, search: str, **kwargs):
    """List task logs."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    if last:
        t = task.last(org_id, namespace, group, key, **kwargs)
        if t:
            return t.log
        else:
            return
    else:
        return task.logs(org_id, namespace, group, key, search, **kwargs)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
@click.option(
    "--states",
    "-s",
    type=str,
    required=False,
    default="Success",
    help="Comma separated states to wait for. Valid values: Success, Error, Canceled, Running, Init.",
)
@cli.wait
def wait(org: str, namespace: str, group: str, smart_path: str, wait: str, states: str, **kwargs):
    """Wait for a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    return task.wait(org_id=org_id, namespace=namespace, group=group, key=key, wait=wait, states=states, **kwargs)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@cli.confirm
def cancel(org: str, namespace: str, group: str, smart_path: str, confirm: bool, **kwargs):
    """Cancel a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Cancel task {namespace}/{group}/{key}?", abort=True)
        else:
            click.confirm(f"Cancel task {namespace}/{group}/{key}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.cancel(org_id, namespace, group, key)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@click.option("--execution-id", "-e", type=str, required=True)
@cli.confirm
def retrigger(org: str, namespace: str, group: str, smart_path: str, execution_id: str, confirm: bool, **kwargs):
    """Retrigger a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Retrigger task {namespace}/{group}/{key}/{execution_id}", abort=True)
        else:
            click.confirm(f"Retrigger task {namespace}/{group}/{key}/{execution_id}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.retrigger(org_id, namespace, group, key, execution_id)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@cli.confirm
def resubmit(org: str, namespace: str, group: str, smart_path: str, confirm: bool, **kwargs):
    """Duplicate the task configuration and submit a new one."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Resubmit task {namespace}/{group}/{key}", abort=True)
        else:
            click.confirm(f"Resubmit task {namespace}/{group}/{key}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.resubmit(org_id, namespace, group, key)


def _parse_task_param(namespace: str, group: str, smart_path: str):
    if smart_path:
        parts = smart_path.split("/")
        if len(parts) == 3:
            if namespace:
                raise CtxpException("Invalid path: Namespace already specified. Avoid using --namespace and namespace in path together.")
            if group:
                raise CtxpException("Invalid path: Group already specified. Avoid using --group and group in path together.")

            namespace, group, key = parts
            if not namespace:
                raise CtxpException("Invalid path: Missing namespace. Valid example: <namespace>/<group>/<key>.")
            if not group:
                raise CtxpException("Invalid path: Missing group. Valid example: <namespace>/<group>/<key>.")
            if not key:
                raise CtxpException("Invalid path: Missing key. Valid example: <namespace>/<group>/<key>.")

            recent.set("task.namespace", namespace)
            recent.set("task.group", group)
            recent.set("task.key", key)
        elif len(parts) == 2:
            namespace = recent.require("task.namespace", namespace)
            group = recent.require("task.group", parts[0])
            key = recent.require("task.key", parts[1])
        elif len(parts) == 1:
            namespace = recent.require("task.namespace", namespace)
            group = recent.require("task.group", group)
            key = recent.require("task.key", parts[0])
    else:
        namespace = recent.require("task.namespace", namespace)
        group = recent.get("task.group")
        if not group:
            group = "default"
        key = recent.require("task.key", None)

    return namespace, group, key
