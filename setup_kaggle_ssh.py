import random
import string
import subprocess
import sys

from pyngrok import conf, ngrok

if len(sys.argv) != 2:
    print("Usage: python setup_kaggle_ssh.py <ngrok_authtoken>")
    exit(1)

ngrok_auth_token = sys.argv[1]

def generate_random_password(length=16):
    characters = (string.ascii_letters + string.digits + "!@#$%^*()-_=+{}[]<>.,?")
    return ''.join(random.choices(characters, k=length))

password = generate_random_password()
print(f"Setting password for root user: {password}")
subprocess.run(f"echo 'root:{password}' | sudo chpasswd", shell=True, check=True)

conf.get_default().auth_token = ngrok_auth_token
conf.get_default().region = 'ap'

# start ngrok tunnel
# Open ngrok tunnel on Jupyter's default port 8888
tunnel = ngrok.connect(8888, "http")
ngrok_url = tunnel.public_url

if ngrok_url:
    # Extract the hostname from the URL
    if '://' in ngrok_url:
        hostname = ngrok_url.split("://")[1]
    else:
        hostname = ngrok_url
    
    print(f"ngrok tunnel opened at: {ngrok_url}")
    print("You can access the Jupyter notebook at the following URL:")
    print(f"{ngrok_url}")
    sys.stdout.flush()
else:
    print("Failed to start ngrok tunnel.")
    exit(1)

ngrok_process = ngrok.get_ngrok_process()
try:
    # hit ctrl-c to stop ngrok, or just power off the noteboko
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("Shutting down ngrok tunnel")
    ngrok.kill()
