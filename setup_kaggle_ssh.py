import random
import string
import subprocess
import sys
from pyngrok import conf, ngrok

if len(sys.argv) != 2:
    print("Usage: python setup_kaggle_ssh.py <ngrok_authtoken>")
    exit(1)

ngrok_auth_token = sys.argv[1]

def generate_secure_jupyter_password():
    """ Generate a random, strong Jupyter notebook password """
    characters = string.ascii_letters + string.digits + "!@#$%^*()-_=+{}[]<>.,?"
    return ''.join(random.choices(characters, k=16))

jupyter_password = generate_secure_jupyter_password()
print(f"Setting password for Jupyter Notebook: {jupyter_password}")

# Secure Jupyter by setting a password (requires Jupyter installed)
subprocess.run(f"jupyter notebook --generate-config -y", shell=True, check=True)
subprocess.run(
    f"echo \"c.NotebookApp.password = u'$(python3 -c \"from notebook.auth import passwd; print(passwd('{jupyter_password}'))\")'\" >> ~/.jupyter/jupyter_notebook_config.py",
    shell=True,
    check=True
)

# Configure and start ngrok
conf.get_default().auth_token = ngrok_auth_token
conf.get_default().region = 'eu'  # Change region as needed

tunnel = ngrok.connect(8888, "http")
ngrok_url = tunnel.public_url

if ngrok_url:
    print(f"ngrok tunnel opened at: {ngrok_url}")
    print("Access Jupyter Notebook at the following URL (login required):")
    print(f"{ngrok_url}")
    sys.stdout.flush()
else:
    print("Failed to start ngrok tunnel.")
    exit(1)

ngrok_process = ngrok.get_ngrok_process()
try:
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("Shutting down ngrok tunnel")
    ngrok.kill()
