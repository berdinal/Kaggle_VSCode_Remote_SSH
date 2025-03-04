import sys
from pyngrok import conf, ngrok

if len(sys.argv) != 2:
    print("Usage: python setup_kaggle_ssh.py <ngrok_authtoken>")
    sys.exit(1)

ngrok_auth_token = sys.argv[1]

# Inform the user that key‐based authentication is assumed.
print("Configuring ngrok tunnel for SSH access using key-based authentication.")
print("Ensure that your SSH daemon is configured to use public-key authentication only.")

# Configure ngrok with the provided token and region.
conf.get_default().auth_token = ngrok_auth_token
conf.get_default().region = 'eu'

# Start the ngrok tunnel on port 22 using TCP.
try:
    tunnel = ngrok.connect("22", "tcp")
except Exception as e:
    print("Failed to start ngrok tunnel:", e)
    sys.exit(1)

ngrok_url = tunnel.public_url

if ngrok_url:
    try:
        # Expected format is: tcp://<hostname>:<port>
        _, address = ngrok_url.split("://")
        hostname, port = address.split(":")
        print(f"ngrok tunnel opened at: {ngrok_url}")
        print("To connect via SSH, use the following command:")
        print(f"ssh root@{hostname} -p {port}")
    except Exception as e:
        print("Error parsing ngrok URL:", e)
        sys.exit(1)
else:
    print("Failed to start ngrok tunnel.")
    sys.exit(1)

print("Press Ctrl-C to terminate the tunnel.")

try:
    # Wait for the tunnel process to finish (or until interrupted)
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("Shutting down ngrok tunnel")
    ngrok.kill()
