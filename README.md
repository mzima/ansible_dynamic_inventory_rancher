# Dynamic Ansible Inventory for Rancher

Query a [Rancher](https://github.com/rancher/rancher) management cluster to know about available nodes, that belong to this cluster and also to imported Kubernetes clusters.
See the [documentation on dynamic inventory](http://docs.ansible.com/ansible/intro_dynamic_inventory.html) for more details on the 'dynamic inventory' concept.

## Prerequisites

The Ansible dynamic inventory script for Rancher was tested with:

* Ansible 2.7+
* Rancher 2.4.x
* Python 3

Other Rancher versions might work as well depending on API changes.

## Getting started

#### inventory.ini

First you have to provide the API url and the credentials by creating the `inventory.ini` file

```
[main]
rancher_url = https://rancher.example.com
rancher_token = token-abc:key1234567890
``` 

#### inventory.py

The `inventory.py` script queries the Rancher management cluster API to present the results to Ansible as an inventory.
There is currently no caching implemented. Make sure to make the file executable.

```
ansible all -m ping -i inventory.py
```

For debugging reasons the `inventory.py` can also started without Ansible:

```
./inventory.py --list
```

#### Inventory example output

The local cluster inventory should look like this. This inventory script also supports imported clusters.

```
{
  "_meta": {
    "hostvars": {
      "node1": {
        "roles": [
          "controlplane",
          "worker",
          "etcd"
        ],
        "host_state": "active",
        "host_id": "local:machine-v9bcn",
        "cluster_name": "local",
        "cluster_id": "local",
        "labels": {
          "beta.kubernetes.io/arch": "amd64",
          "beta.kubernetes.io/os": "linux",
          "kubernetes.io/arch": "amd64",
          "kubernetes.io/hostname": "node1",
          "kubernetes.io/os": "linux",
          "node-role.kubernetes.io/controlplane": "true",
          "node-role.kubernetes.io/etcd": "true",
          "node-role.kubernetes.io/worker": "true",
          "persistence": "statefull"
        }
      },
      "node2": {
        "roles": [
          "controlplane",
          "worker",
          "etcd"
        ],
        "host_state": "active",
        "host_id": "local:machine-v9bcn",
        "cluster_name": "local",
        "cluster_id": "local",
        "labels": {
          "beta.kubernetes.io/arch": "amd64",
          "beta.kubernetes.io/os": "linux",
          "kubernetes.io/arch": "amd64",
          "kubernetes.io/hostname": "node2",
          "kubernetes.io/os": "linux",
          "node-role.kubernetes.io/controlplane": "true",
          "node-role.kubernetes.io/etcd": "true",
          "node-role.kubernetes.io/worker": "true",
          "persistence": "statefull"
        }
      },
      "node3": {
        "roles": [
          "controlplane",
          "worker",
          "etcd"
        ],
        "host_state": "active",
        "host_id": "local:machine-v9bcn",
        "cluster_name": "local",
        "cluster_id": "local",
        "labels": {
          "beta.kubernetes.io/arch": "amd64",
          "beta.kubernetes.io/os": "linux",
          "kubernetes.io/arch": "amd64",
          "kubernetes.io/hostname": "node3",
          "kubernetes.io/os": "linux",
          "node-role.kubernetes.io/controlplane": "true",
          "node-role.kubernetes.io/etcd": "true",
          "node-role.kubernetes.io/worker": "true",
          "persistence": "statefull"
        }
      }
    }
  },
  "all": {
    "vars": {
      "api_url_base": "https://rancher.example.com/v3"
    }
  },
  "local": {
    "hosts": [
      "node1",
      "node2",
      "node3"
    ],
    "vars": {
      "controller_manager_healthy": true,
      "etcd_0_healthy": true,
      "etcd_1_healthy": true,
      "etcd_2_healthy": true,
      "description": "",
      "driver": "imported",
      "id": "local",
      "istioEnabled": false,
      "nodeCount": 3,
      "state": "active"
    }
  }
}
```