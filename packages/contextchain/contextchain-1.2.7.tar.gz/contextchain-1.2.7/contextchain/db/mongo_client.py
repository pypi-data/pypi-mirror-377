from pymongo import MongoClient
import subprocess
import os
import time
from pathlib import Path
import logging
import atexit

logger = logging.getLogger(__name__)

def get_mongo_client(uri="mongodb://localhost:27017", db_name=None):
    """
    Get a MongoDB client instance, with fallback to starting a local MongoDB instance.

    Args:
        uri (str): MongoDB connection URI (e.g., 'mongodb://localhost:27017')
        db_name (str, optional): Database name (not used for connection, for reference only).

    Returns:
        MongoClient: Configured MongoDB client instance.

    Raises:
        Exception: If connection fails and local MongoDB cannot be started.
    """
    def cleanup_mongod(process):
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
                logger.info("Local MongoDB instance terminated.")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning("Local MongoDB instance forcefully terminated.")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        client.server_info()  # Test connection
        logger.info(f"Connected to MongoDB at {uri}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB at {uri}: {e}")
        logger.info("Attempting to start a local MongoDB instance...")
        
        data_dir = Path("/tmp/contextchain_mongodb")
        data_dir.mkdir(exist_ok=True)
        try:
            # Set permissions to ensure MongoDB can write to the directory
            os.chmod(data_dir, 0o755)
        except PermissionError as pe:
            logger.error(f"Failed to set permissions on {data_dir}: {pe}")
            raise Exception(f"Failed to set permissions on {data_dir}: {pe}")

        mongod_process = subprocess.Popen([
            "mongod",
            "--dbpath", str(data_dir),
            "--port", "27017",
            "--bind_ip", "127.0.0.1"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Register cleanup at exit
        atexit.register(cleanup_mongod, mongod_process)

        # Poll for MongoDB readiness (up to 10 seconds)
        max_attempts = 20
        attempt_interval = 0.5  # seconds
        for attempt in range(max_attempts):
            try:
                client = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
                client.server_info()
                logger.info("Local MongoDB instance started successfully.")
                return client
            except Exception:
                time.sleep(attempt_interval)
                continue

        # If we reach here, MongoDB failed to start
        cleanup_mongod(mongod_process)
        raise Exception(f"Failed to start local MongoDB after {max_attempts * attempt_interval} seconds")