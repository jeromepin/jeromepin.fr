---
title: "Esctl: managing elasticsearch from the command line"
date: 2019-09-22T22:08:00+01:00
lang: en
taxonomies:
  tags: []
extra:
  sources: []
  footnotes: []
---

During my month of unemployment, I spent time thinking on how I had tackled technical problems in my last year-and-half of work. The best part of my day-to-day mission was to ensure our Elasticsearch clusters were healthy, secured and efficient. To that end, I was using a combination of tools:

* raw `curl` commands,
* bash scripts I wrote,
* graphical interfaces,
* Prometheus monitoring and alerting,
* Some automation,
* commands embedded in SaltStack

It's easy to see there is no common way to manage those clusters, and I was relying on a bunch of disparate stuff.

## The problem

The issue does not come from Elasticsearch itself but is inherent to any software that exposes an HTTP API to manage itself: curl-of-the-death.

Here are some commands I used to run on a regular basis (examples come from [Elasticsearch's documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)).

#### List indices

```bash,linenos
$ curl -X GET "localhost:9200/_cat/indices"
yellow open foo VrIiXmIRRA6BNP5JWaXKqA 1 1 0 0 283b 283b
```

#### Change the number of replicas of a given index

```bash,linenos
$ curl -X PUT "localhost:9200/twitter/_settings?pretty" -H 'Content-Type: application/json' -d'
{
    "index" : {
        "number_of_replicas" : 2
    }
}
'
```

#### Reset a index's refresh interval to its default value

```bash,linenos
$ curl -X PUT "localhost:9200/twitter/_settings?pretty" -H 'Content-Type: application/json' -d'
{
    "index" : {
        "refresh_interval" : null
    }
}
'
```

#### Pretty-print cluster stats

```bash,linenos
$ curl -X GET "localhost:9200/_cluster/stats"
{
    "_nodes": {
        "total": 1,
        "successful": 1,
        "failed": 0
    },
    ...
    "nodes": {
        "count": {
            "total": 1,
            "data": 1,
            "coordinating_only": 0,
            "master": 1,
            "ingest": 1
        },
        "versions": [
            "7.2.1"
        ],
        "jvm": {
            "max_uptime_in_millis": 1565394,
            "versions": [
                {
                    "version": "12.0.1",
                    "vm_name": "OpenJDK 64-Bit Server VM",
                    "vm_version": "12.0.1+12",
                    "vm_vendor": "Oracle Corporation",
                    "bundled_jdk": true,
                    "using_bundled_jdk": true,
                    "count": 1
                }
            ],
            "mem": {
                "heap_used_in_bytes": 128029720,
                "heap_max_in_bytes": 1056309248
            },
            "threads": 31
        },
        ...
    }
}
```

#### Reroute shard 0 of index 'test' from node1 to node2

```bash,linenos
$ curl -X POST "localhost:9200/_cluster/reroute?pretty" -H 'Content-Type: application/json' -d'
{
    "commands" : [
        {
            "move" : {
                "index" : "test", "shard" : 0,
                "from_node" : "node1", "to_node" : "node2"
            }
        }
    ]
}
'
```

#### Change cluster's transient setting 'indices.recovery.max_bytes_per_sec' to 20mb

```bash,linenos
$ curl -X PUT "localhost:9200/_cluster/settings?flat_settings=true&pretty" -H 'Content-Type: application/json' -d'
{
    "transient" : {
        "indices.recovery.max_bytes_per_sec" : "20mb"
    }
}
'
```


Commands are short, but if I need to pass URL parameters, content type, HTTP verb and a full JSON body, they are no longer short...

Of course, I could use some bash alias to hide the `-H 'Content-Type: application/json'`, or maybe use the excellent [HTTPie](https://httpie.org/) but the biggest pain comes from the JSON body!


## Requirements

I needed a tool which could abstract all those long curl commands and could be flexible enough. After looking on the Internet, it appeared the few tools already written didn't support commands I needed. Thus, I decided to write my own, and I came with a list of requirements:

| Requirement | Solution |
|------------|------------|
| Easy and fast to write | Python : high-level, easy to read and write, I know it well |
| Fast to use | Command-line |
| Abstract/hide params | Command-line params and integrated help ! I don't want to remember what verb to use, what URL params to give, what to put in the JSON body, etc... |
| Don't spend time on building CLI | [Openstack's Cliff](https://github.com/openstack/cliff) |
| Easy to switch cluster, without remembering long server name | Config file |
| Each cluster may have different setup (ssl, auth, etc...) | Config file |
| Nice and pretty output | [Cliff](https://github.com/openstack/cliff) comes with [PrettyTable](https://pypi.org/project/PrettyTable/) |
| Inspiration | [Openstack's CLI](https://github.com/openstack/python-openstackclient) and [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) |


## The solution

I ended up writing [esctl](https://github.com/jeromepin/esctl). It checks all my requirements and it's very easy to add new features by inheriting a class based on the output type.

{{figure(src="/images/esctl-CLI-design-tree.svg" title="Esctl subcommands taxonomy" alt="Esctl subcommands taxonomy")}}

It relies on a config file (inspired by `kubectl`) to declare settings (global and cluster-wide), clusters, users and contexts (an association of a user and a cluster) :

```yaml,linenos
settings:
  no_check_certificate: true
  max_retries: 0
  timeout: 20

clusters:
  localhost:
    servers:
    - http://localhost:9200

  foo01-prd-sfo:
    servers:
    - https://master01-foo01-prd-sfo1.example.com
    - https://master02-foo01-prd-sfo2.example.com
    - https://master03-foo01-prd-sfo3.example.com
    settings:
      timeout: 60

users:
  jerome:
    username: jerome
    password: P@ssw0rD

contexts:
  localhost:
    cluster: localhost

  production:
    user: jerome
    cluster: foo01-prd-sfo

default-context: localhost
```

Esctl provides a lot of commands and subcommands to manage Elasticsearch:

```
usage: esctl [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug] [--context CONTEXT]

esctl

optional arguments:
  --version            show program's version number and exit
  -v, --verbose        Increase verbosity of output. Can be repeated.
  -q, --quiet          Suppress output except warnings and errors.
  --log-file LOG_FILE  Specify a file to log output. Disabled by default.
  -h, --help           Show help message and exit.
  --debug              Show tracebacks on errors.
  --context CONTEXT    Context to use

Commands:
  cat allocation                     Show shard allocation.
  cluster allocation explain         Provide explanations for shard allocations in the cluster.
  cluster health                     Retrieve the cluster health.
  cluster routing allocation enable  Change the routing allocation status.
  cluster stats                      Retrieve the cluster status.
  complete                           print bash completion command (cliff)
  config context list                List all contexts.
  help                               print detailed help for another command (cliff)
  index close                        Close an index.
  index create                       Create an index.
  index delete                       Delete an index.
  index list                         List all indices.
  index open                         Open an index.
  logging get                        Get a logger value.
  logging reset                      Reset a logger value.
  logging set                        Set a logger value.
  node hot-threads                   Print hot threads on each nodes.
  node list                          List nodes.
```

It allows to dramatically shorten previously shown commands :

#### List indices

```bash,linenos
$ esctl index list
+-------+--------+--------+------------------------+---------+---------+------------+--------------+------------+--------------------+
| Index | Health | Status | UUID                   | Primary | Replica | Docs Count | Docs Deleted | Store Size | Primary Store Size |
+-------+--------+--------+------------------------+---------+---------+------------+--------------+------------+--------------------+
| foo   | yellow | open   | VrIiXmIRRA6BNP5JWaXKqA | 1       | 1       | 0          | 0            | 283b       | 283b               |
+-------+--------+--------+------------------------+---------+---------+------------+--------------+------------+--------------------+
```

#### Change the number of replicas of a given index

_Not implemented yet. Would look like :_

```bash,linenos
$ esctl index settings set number_of_replicas 2 --index=twitter
```

#### Reset a index's refresh interval to its default value

_Not implemented yet. Would look like :_

```bash,linenos
$ esctl index settings reset refresh_interval --index=twitter
```

#### Pretty-print cluster stats

```bash,linenos
$ esctl cluster stats
+------------------------------------------------+------------------------------+
| Attribute                                      |                        Value |
+------------------------------------------------+------------------------------+
| _nodes.failed                                  |                            0 |
| _nodes.successful                              |                            1 |
| _nodes.total                                   |                            1 |
...
| nodes.count.coordinating_only                  |                            0 |
| nodes.count.data                               |                            1 |
| nodes.count.ingest                             |                            1 |
| nodes.count.master                             |                            1 |
| nodes.count.total                              |                            1 |
| nodes.discovery_types.single-node              |                            1 |
| nodes.fs.available_in_bytes                    |                  48388599808 |
| nodes.fs.free_in_bytes                         |                  51605315584 |
| nodes.fs.total_in_bytes                        |                  62725623808 |
| nodes.jvm.max_uptime_in_millis                 |                      1565394 |
| nodes.jvm.mem.heap_max_in_bytes                |                   1056309248 |
| nodes.jvm.mem.heap_used_in_bytes               |                    128029720 |
| nodes.jvm.threads                              |                           31 |
| nodes.jvm.versions[0].bundled_jdk              |                         True |
| nodes.jvm.versions[0].count                    |                            1 |
| nodes.jvm.versions[0].using_bundled_jdk        |                         True |
| nodes.jvm.versions[0].version                  |                       12.0.1 |
| nodes.jvm.versions[0].vm_name                  |     OpenJDK 64-Bit Server VM |
| nodes.jvm.versions[0].vm_vendor                |           Oracle Corporation |
| nodes.jvm.versions[0].vm_version               |                    12.0.1+12 |
...
| status                                         |                       yellow |
| timestamp                                      |                1565893455640 |
+------------------------------------------------+------------------------------+
```

#### Reroute shard 0 of index 'test' from node1 to node2

_Not implemented yet_

#### Change cluster's transient setting 'indices.recovery.max_bytes_per_sec' to 20mb

_Not implemented yet. Would look like :_

```bash,linenos
$ esctl cluster settings set --transient indices.recovery.max_bytes_per_sec 20mb
```


## What a subcommand look likes

I created 3 output class based on Cliff's ones:

* `EsctlCommand` : Doesn't expect any output
* `EsctlLister` : Expect a list of elements in order to create a multi-columns table
* `EsctlShowOne` : Expect a key-value list to create a two-columns table

To add a new subcommand, I only need to choose the output class (and inherit my class from it) and write the `take_action` method:

```python,linenos
def take_action(self, parsed_args):
    """Generate or retrieve data to be displayed.

    Arguments:
        parsed_args {argparse.Namespace} -- Arguments from the command line.

    Returns:
        Any -- The data to be displayed, as specified by Cliff
    """

    return data
```

Here is, as a sample, the class associated to the `esctl cluster health` command:

```python,linenos
class ClusterHealth(EsctlShowOne):
    """Retrieve the cluster health."""

    def take_action(self, parsed_args):
        # Retrieve the cluster health using the appropriate elasticsearch-py function. Then order the output and sort it
        health = self._sort_and_order_dict(Esctl._es.cluster.health())

        # Add coloration of the "status" (RED, YELLOW, GREEN) key based on it's value
        health["status"] = Color.colorize(
            health.get("status"), getattr(Color, health.get("status").upper())
        )

        # Return a tuple of tuple. It will lead to a two-column table : "Attribute" and "Value"
        return (tuple(health.keys()), tuple(health.values()))
```

Which will display :

```
+----------------------------------+----------------+
| Field                            | Value          |
+----------------------------------+----------------+
| active_primary_shards            | 0              |
| active_shards                    | 0              |
| active_shards_percent_as_number  | 100.0          |
| cluster_name                     | docker-cluster |
| delayed_unassigned_shards        | 0              |
| initializing_shards              | 0              |
| number_of_data_nodes             | 1              |
| number_of_in_flight_fetch        | 0              |
| number_of_nodes                  | 1              |
| number_of_pending_tasks          | 0              |
| relocating_shards                | 0              |
| status                           | green          |
| task_max_waiting_in_queue_millis | 0              |
| timed_out                        | False          |
| unassigned_shards                | 0              |
+----------------------------------+----------------+
```

Instead of :

```json,linenos
{
  "cluster_name" : "docker-cluster",
  "status" : "green",
  "timed_out" : false,
  "number_of_nodes" : 1,
  "number_of_data_nodes" : 1,
  "active_primary_shards" : 0,
  "active_shards" : 0,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 0,
  "delayed_unassigned_shards" : 0,
  "number_of_pending_tasks" : 0,
  "number_of_in_flight_fetch" : 0,
  "task_max_waiting_in_queue_millis" : 0,
  "active_shards_percent_as_number" : 100.0
}
```