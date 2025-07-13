import subprocess
import webbrowser
import time
import os
import shutil

# Define Docker config
image_name = "mistral-7b"
container_name = "jolly_shtern"

def is_docker_running():
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def start_docker_desktop():
    docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if os.path.exists(docker_path):
        print("🚀 Starting Docker Desktop...")
        subprocess.Popen([docker_path])
        print("⏳ Waiting for Docker to be ready...")
        for _ in range(30):  # Wait max 30 * 2 = 60 seconds
            if is_docker_running():
                return True
            time.sleep(2)
    return False

def start_container():
    print("🛠️  Starting Docker container...")
    result = subprocess.run(["docker", "start", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode != 0:
        print("🧱 Container not found. Running new container...")
        subprocess.run([
            "docker", "run", "-d",
            "--restart=unless-stopped",
            "-v", f"{os.getcwd()}:/app",
            "-p", "8000:8000",
            "--name", container_name,
            image_name
        ], check=True)

def start_http_server_and_open_browser():
    print("🌐 Starting local server for chat.html...")
    subprocess.Popen(["python", "-m", "http.server", "5500"], cwd=os.path.join(os.getcwd(),))
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5500/chat.html")

# --- Main Execution ---
if not is_docker_running():
    if not start_docker_desktop():
        print("❌ Failed to start Docker. Please start it manually.")
        exit(1)

start_container()
time.sleep(5)
start_http_server_and_open_browser()
