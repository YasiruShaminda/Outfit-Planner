import os
import sys
import subprocess

def setup_directories():
    """Create necessary directories for storing data"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import google.generativeai
        import numpy
        from PIL import Image
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Installing requirements...")
        subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False

def main():
    """Main function to run the application"""
    print("Setting up AI Personal Stylist Assistant...")
    setup_directories()
    
    if not check_requirements():
        print("Requirements installed. Please run the script again.")
        sys.exit(0)
    
    # Check if .env file exists, if not create from example
    if not os.path.exists(".env") and os.path.exists("env.example"):
        print("\nNOTICE: Creating .env file from template.")
        print("You need to edit the .env file and add your Gemini API key.")
        with open("env.example", "r") as f_in, open(".env", "w") as f_out:
            f_out.write(f_in.read())
    
    print("\nStarting the Streamlit application...")
    subprocess.call(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main() 