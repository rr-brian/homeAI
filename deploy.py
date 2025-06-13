import os
import sys
import subprocess

def main():
    print("Starting deployment script...")
    
    # Print current directory and contents
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir(os.getcwd())}")
    
    # Install requirements
    print("Installing requirements...")
    if os.path.exists('requirements.txt'):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    else:
        print("requirements.txt not found!")
    
    # Install the local package
    print("Installing local package...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', '.'])
    
    print("Deployment completed successfully!")

if __name__ == '__main__':
    main()
