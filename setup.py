import subprocess
import time
import sys
import requests
from requests.exceptions import ConnectionError


def is_docker_running():
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_api_status():
    try:
        print("\n🔍 Checking API status at http://localhost:8000/docs")
        response = requests.get("http://localhost:8000/docs")
        print(f"📡 Response status code: {response.status_code}")
        return response.status_code == 200
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def start_docker():
    print("\n🚀 Starting Docker containers...")
    if not is_docker_running():
        print("❌ Docker is not running!")
        print("💡 Please start Docker Desktop and try again")
        return False

    try:
        print("📦 Starting container...")
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        print("✅ Docker container started")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker error: {e}")
        return False


def run_tests():
    print("\n🧪 Running pytest tests...")
    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v"], capture_output=True, text=True
        )
        print("\n📋 Test Results:")
        print("=" * 80)
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def safe_docker_down():
    """Safely try to stop Docker containers"""
    if is_docker_running():
        try:
            subprocess.run(["docker", "compose", "down"], check=True)
        except subprocess.CalledProcessError:
            pass  # Ignore errors during shutdown


if __name__ == "__main__":
    try:
        if not start_docker():
            print("❌ Failed to start Docker")
            safe_docker_down()
            sys.exit(1)

        print("\n⏳ Waiting 5 seconds before checking API...")
        time.sleep(5)

        if check_api_status():
            print("\n✅ API is responding!")

            if run_tests():
                print("\n✅ All tests passed!")
                print("\n💡 API container will keep running.")
                print("ℹ️  Use 'docker compose down' when you want to stop it.")
            else:
                print("\n❌ Tests failed!")
                print("\n🛑 Stopping containers due to test failure...")
                safe_docker_down()
                sys.exit(1)
        else:
            print("\n❌ API is not responding!")
            print("\n📋 Docker logs:")
            subprocess.run(["docker", "logs", "api-test"])
            print("\n🛑 Stopping containers due to API failure...")
            safe_docker_down()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        safe_docker_down()
