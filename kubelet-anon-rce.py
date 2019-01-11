import argparse
import requests
import urllib3
import ssl
from websocket import create_connection
from urllib.parse import urljoin
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BASE_URL = 'https://{target}:{port}/'
EXEC_PATH = '/exec/{namespace}/{pod}/{container}'
READ_URL = 'wss://{target}:{port}/'
PARAMS = {
    'input': 1,
    'output': 1,
    'tty': 1
}


def get_args():
    parser = argparse.ArgumentParser(
        description='Run commands against a Kubelet endpoint.')
    parser.add_argument('--port', default=10250,
                        help='kubelet port, default: 10250')
    parser.add_argument('-t', '--target', required=True,
                        help='Kubernetes worker node IP address')
    parser.add_argument('-n', '--namespace', required=True,
                        help='namespace, ie: \'default\'')
    parser.add_argument('-p', '--pod', required=True,
                        help='pod name, ie: \'dh-nginx-8484b69674-z9tzl\'')
    parser.add_argument('-c', '--container', required=True,
                        help='container name, ie:\'nginx\'')
    parser.add_argument('-x', '--exec', required=True,
                        help='command to execute, ie: \'ls /tmp\'')
    
    return parser.parse_args()


def exec(target, port, namespace, pod, container, command):
    """
       Runs a command in the given container and returns the path to poll for
       results.
    """
    path = EXEC_PATH.format(port=port,
                            namespace=namespace,
                            pod=pod,
                            container=container)
    url = urljoin(BASE_URL.format(target=target, port=port), path)
    params = {**PARAMS, 'command': command.split()}
    response = requests.get(url, params=params, verify=False,
                            allow_redirects=False)
    return response.headers['location']


def read(target, port, path):
    url = urljoin(READ_URL.format(target=target, port=port), path)
    ws = create_connection(url, sslopt={'cert_reqs': ssl.CERT_NONE})
    output = ''
    while True:
        try:
            output += ws.recv().decode('utf-8')
        except:
            ws.close()
            break
    return output


def main():
    args = get_args()
    cri =  exec(args.target, args.port, args.namespace, args.pod, args.container,
                args.exec)
    output = read(args.target, args.port, cri)
    print(output)


if __name__ == '__main__':
    main()
