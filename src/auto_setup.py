import subprocess
import sys

def run_command(command):
    try:
        print(f"Running: {command}")

        subprocess.run(
            command,
            shell=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        print("Setup command failed:", e)
        sys.exit(1)

def setup_project():

    print("Starting hackathon auto-setup...")

    # Install dependencies
    run_command("pip install fastapi")
    run_command("pip install uvicorn")
    run_command("pip install requests")
    run_command("pip install python-dotenv")
    run_command("pip install numpy")
    run_command("pip install scikit-learn")
    run_command("pip install sentence-transformers")

    print("Setup complete!")

if __name__ == "__main__":
    setup_project()