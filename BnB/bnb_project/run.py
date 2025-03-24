#!/usr/bin/env python3

"""

Budget Buddy - Application Launcher

This script launches both the Flask backend and Tkinter frontend for the Budget Buddy application.

"""

import os
import sys
import subprocess
import time
import threading
import logging
import requests  # Import the requests library

# Configure logging
logging.basicConfig(
    filename="run.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Determine the project directory
if getattr(sys, 'frozen', False):
    project_dir = os.path.dirname(sys.executable)
else:
    project_dir = os.path.dirname(os.path.abspath(__file__))

# Paths to backend and frontend scripts
BACKEND_PATH = os.path.join(project_dir, "backend.py")
FRONTEND_PATH = os.path.join(project_dir, "frontend.py")

# Backend server details
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5000
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Global variables for processes
backend_process = None
frontend_process = None

def is_backend_running():
    """Check if the backend is running by sending a request to /health."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200 and response.json().get("status") == "ok"
    except requests.RequestException:
        return False

def start_backend():
    """Start the Flask backend server"""
    global backend_process
    try:
        if not os.path.exists(BACKEND_PATH):
            logger.error(f"Backend script not found at {BACKEND_PATH}")
            print(f"Error: Backend script not found at {BACKEND_PATH}")
            return False

        if is_backend_running():
            print("Backend is already running.")
            logger.info("Backend is already running.")
            return True

        print(f"Starting Flask backend at {BACKEND_URL}...")
        logger.info(f"Starting Flask backend at {BACKEND_URL}")

        backend_process = subprocess.Popen(
            [sys.executable, BACKEND_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for the backend to become healthy, with a timeout
        max_wait_time = 30  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            if is_backend_running():
                print("Flask backend started successfully.")
                logger.info("Backend started successfully")
                return True
            time.sleep(1)  # Check every second

        # If we reach here, the backend didn't become healthy
        stdout, stderr = backend_process.communicate()
        logger.error("Backend failed to start (health check failed)")
        logger.error(f"Backend stdout: {stdout}")
        logger.error(f"Backend stderr: {stderr}")
        print("Error: Backend failed to start. Check run.log for details.")
        print(f"Backend stdout: {stdout}")
        print(f"Backend stderr: {stderr}")
        return False

    except Exception as e:
        logger.error(f"Failed to start backend: {str(e)}")
        print(f"Error starting backend: {str(e)}")
        return False

def start_frontend():
    """Start the Tkinter frontend application"""
    global frontend_process
    try:
        if not os.path.exists(FRONTEND_PATH):
            logger.error(f"Frontend script not found at {FRONTEND_PATH}")
            print(f"Error: Frontend script not found at {FRONTEND_PATH}")
            return False

        print("Starting Tkinter frontend...")
        logger.info("Starting Tkinter frontend")

        frontend_process = subprocess.Popen(
            [sys.executable, FRONTEND_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(1)  # Give the frontend time to start

        if frontend_process.poll() is not None:  # Check if the process has terminated
            stdout, stderr = frontend_process.communicate()
            logger.error("Frontend failed to start")
            logger.error(f"Frontend stdout: {stdout}")
            logger.error(f"Frontend stderr: {stderr}")
            print("Error: Frontend failed to start. Check run.log for details.")
            return False

        print("Tkinter frontend started successfully.")
        logger.info("Frontend started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start frontend: {str(e)}")
        print(f"Error starting frontend: {str(e)}")
        return False

def stop_processes():
    """Stop all running processes"""
    global backend_process, frontend_process

    for process, name in [(frontend_process, "frontend"), (backend_process, "backend")]:
        if process:
            print(f"Terminating {name}...")
            logger.info(f"Terminating {name}")
            try:
                process.terminate()
                process.wait(timeout=5)  # Increased timeout
                logger.info(f"{name.capitalize()} terminated successfully")
            except subprocess.TimeoutExpired:
                logger.warning(f"Failed to terminate {name} gracefully, killing...")
                process.kill()  # Forcefully kill if terminate fails
                logger.info(f"{name.capitalize()} killed")
            except Exception as e:
                logger.warning(f"Failed to terminate {name}: {str(e)}")
            finally:
                globals()[f"{name}_process"] = None  # Clear the global variable

    print("All processes terminated.")
    logger.info("All processes terminated")

def monitor_frontend():
    """Monitor the frontend process and stop the backend when it closes"""
    global frontend_process
    while frontend_process and frontend_process.poll() is None:
        time.sleep(1)

    if frontend_process: # Check if frontend_process is not None
        print("Frontend closed. Shutting down backend...")
        logger.info("Frontend closed, shutting down backend")
        stop_processes()
        print("Budget Buddy has been shut down.")
        logger.info("Budget Buddy has been shut down")

def main():
    """Main function to launch the application"""
    print("=" * 50)
    print("Launching Budget Buddy Application")
    print("=" * 50)
    logger.info("Launching Budget Buddy application")

    if not start_backend():
        print("Failed to start backend. Exiting.")
        logger.error("Failed to start backend, exiting")
        sys.exit(1)

    # No need for extra sleep here, backend health check handles it

    if not start_frontend():
        print("Failed to start frontend. Shutting down...")
        logger.error("Failed to start frontend, shutting down")
        stop_processes()
        sys.exit(1)

    print("Budget Buddy is now running!")
    logger.info("Budget Buddy is now running")

    # Start monitoring the frontend in a separate thread
    monitor_thread = threading.Thread(target=monitor_frontend)
    monitor_thread.daemon = True  # Daemonize the thread
    monitor_thread.start()

    try:
        monitor_thread.join()  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Shutting down...")
        logger.info("Keyboard interrupt detected, shutting down")
        stop_processes()
        sys.exit(0)

    print("Budget Buddy launcher has exited.")
    logger.info("Budget Buddy launcher has exited")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application crashed: {str(e)}")
        print(f"Error: Application crashed: {str(e)}")
        sys.exit(1)
