# scripts/install_prerequisites.py

# Placeholder for installing prerequisites (e.g., pyscard, ACR1252U driver)
import subprocess

def install_prerequisites():
    try:
        subprocess.run(['pip', 'install', '-r', 'docs/requirements.txt'], check=True)
        print('Dependencies installed successfully.')
        # TODO: Add logic to check/install ACR1252U driver
    except subprocess.CalledProcessError:
        print('Error installing dependencies.')

if __name__ == '__main__':
    install_prerequisites()
