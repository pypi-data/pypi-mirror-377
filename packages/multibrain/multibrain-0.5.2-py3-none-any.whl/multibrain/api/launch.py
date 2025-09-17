# src/multibrain/api/launch.py

import subprocess


def run_fastapi():
    try:
        subprocess.run(
            [
                "uvicorn",
                "multibrain.api.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running FastAPI: {e}")


if __name__ == "__main__":
    run_fastapi()
