import requests
import argparse

#diagnostics in /tmp
#targetting specific file

def parse_args():
    parser = argparse.ArgumentParser(prog="diagnostics",
                                     usage='%(prog)s [options]',
                                     description='Diagnostics Tool',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-e', '--email', type=str, help='Email address of requester')
    return parser.parse_args()


def run_diagnostics(email):
    with open(f"/tmp/diagnostics.txt") as f:
        output = f.readline().strip()
        print(output)


if __name__ == "__main__":
    args = parse_args()
    run_diagnostics(args.email)
