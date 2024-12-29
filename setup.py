import subprocess
import time
import sys
import requests
from requests.exceptions import ConnectionError


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


def rebuild_docker():
    """Rebuild Docker containers from scratch"""
    print("\n🔄 Rebuilding Docker environment...")
    try:
        # Stop and remove existing containers
        print("🛑 Stopping existing containers...")
        subprocess.run(["docker", "compose", "down"], check=True)
        
        # Remove existing containers
        print("🗑️  Removing old containers...")
        subprocess.run(["docker", "compose", "rm", "-f"], check=True)
        
        # Build without cache
        print("🏗️  Building fresh containers...")
        subprocess.run(["docker", "compose", "build", "--no-cache"], check=True)
        
        # Start new containers
        print("🚀 Starting new containers...")
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        
        print("✅ Docker rebuild complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker rebuild failed: {e}")
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


if __name__ == "__main__":
    try:
        if not rebuild_docker():
            print("❌ Failed to rebuild Docker")
            sys.exit(1)

        print("\n⏳ Waiting 5 seconds before checking API...")
        time.sleep(5)

        if check_api_status():
            print("\n✅ API is responding!")
            
            if run_tests():
                print("\n✅ All tests passed!")
                print("\n💡 API container is running. Showing logs:")
                print("ℹ️  Use Ctrl+C to stop")
                print("\n📋 Container logs:")
                # Follow all logs for now
                subprocess.run(["docker", "compose", "logs", "--follow"], check=True)
            else:
                print("\n❌ Tests failed!")
                print("\n🛑 Stopping containers due to test failure...")
                subprocess.run(["docker", "compose", "down"])
                sys.exit(1)
        else:
            print("\n❌ API is not responding!")
            print("\n📋 Docker logs:")
            subprocess.run(["docker", "compose", "logs"])
            print("\n🛑 Stopping containers due to API failure...")
            subprocess.run(["docker", "compose", "down"])
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        print("🛑 Stopping containers...")
        subprocess.run(["docker", "compose", "down"])
        print("✅ Containers stopped")
