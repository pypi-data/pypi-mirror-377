import os
import subprocess
import tempfile
import bittensor as bt
from .post_install import main as post_install_main
import shutil


def ensure_bb_installed():
    """Ensure bb is installed before verification."""
    bb_path = shutil.which("bb")
    if not bb_path:
        # Check common installation path
        home = os.path.expanduser("~")
        bb_path = os.path.join(home, ".bb", "bb")
        if not os.path.exists(bb_path):
            bt.logging.info("Installing bb (Barretenberg) for proof verification...")
            try:
                post_install_main()
                bt.logging.info("bb installed successfully!")
                # After installation, bb should be at ~/.bb/bb
                if not os.path.exists(bb_path):
                    bt.logging.error(f"bb not found at expected path: {bb_path}")
                    return None
            except Exception as e:
                bt.logging.error(f"Failed to install bb: {e}")
                return None
    return bb_path if os.path.exists(bb_path) else shutil.which("bb")


def verify(proof_hex, public_inputs_hex):
    """
    Verify a zero-knowledge proof using hex string data.

    Args:
        proof_hex (str): Hex string of proof data
        public_inputs_hex (str): Hex string of public inputs data

    Returns:
        bool: True if verification succeeds, False otherwise
    """
    bb_path = ensure_bb_installed()
    if not bb_path:
        bt.logging.error("Failed to install required dependencies for verification")
        return False

    try:
        proof_data = bytes.fromhex(proof_hex)
        public_inputs_data = bytes.fromhex(public_inputs_hex)
    except ValueError as e:
        bt.logging.error(f"Invalid hex data: {str(e)}")
        return False

    vk_path = os.path.join(os.path.dirname(__file__), "circuits", "vk", "vk")
    if not os.path.exists(vk_path):
        bt.logging.error(f"Verification key file not found: {vk_path}")
        return False

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            proof_path = os.path.join(temp_dir, "proof")
            public_inputs_path = os.path.join(temp_dir, "public_inputs")

            with open(proof_path, "wb") as f:
                f.write(proof_data)
            with open(public_inputs_path, "wb") as f:
                f.write(public_inputs_data)

            result = subprocess.run(
                [
                    bb_path,
                    "verify",
                    "-k",
                    vk_path,
                    "-p",
                    proof_path,
                    "-i",
                    public_inputs_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                bt.logging.info("Proof verification successful")
                return True
            else:
                bt.logging.error(f"Proof verification failed: {result.stderr}")
                return False

    except subprocess.TimeoutExpired:
        bt.logging.error("Proof verification timed out")
        return False
    except Exception as e:
        bt.logging.error(f"Error during proof verification: {str(e)}")
        return False
