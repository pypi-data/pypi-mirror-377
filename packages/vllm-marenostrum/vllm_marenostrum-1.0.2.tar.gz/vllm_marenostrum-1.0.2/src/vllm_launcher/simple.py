#!/usr/bin/env python3
"""
Super simple vLLM launcher with nested config support.
Usage: vllm-marenostrum config.yaml [--cuda-devices 0,1,2,3] [--port 8001]
"""
import yaml
import os
import sys
import subprocess
import tempfile
import argparse
import time
import requests


def wait_for_service_ready(port, timeout_seconds=300):
    """Wait for vLLM service to be ready by checking /health endpoint"""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                return True
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            pass
        time.sleep(2)
    return False


def main():
    parser = argparse.ArgumentParser(description="vLLM MareNostrum launcher")
    parser.add_argument("config", help="Path to config YAML file")
    parser.add_argument("--cuda-devices", help="Comma-separated CUDA devices (overrides config)")
    parser.add_argument("--port", type=int, help="Port number (overrides config)")
    parser.add_argument("--tensor-parallel-size", type=int, help="Tensor parallel size (overrides config)")
    parser.add_argument("--wait-for-ready", action="store_true", help="Wait for service to be ready before exiting")
    parser.add_argument("--background", action="store_true", help="Start in background and exit after ready (implies --wait-for-ready)")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds for health check (default: 300)")

    args, unknown_args = parser.parse_known_args()

    # Check config file exists
    if not os.path.exists(args.config):
        print(f"ERROR: Config file {args.config} not found")
        sys.exit(1)

    # Load config file
    with open(args.config) as f:
        config = yaml.safe_load(f)

    # Extract sections
    vllm_config = config.get('vllm', {})
    launcher_config = config.get('launcher', {})

    # Handle launcher-specific parameters
    cuda_devices = args.cuda_devices or launcher_config.get('cuda_devices')
    if cuda_devices:
        if cuda_devices == "cpu":
            # CPU configuration
            vllm_config['device'] = 'cpu'
            print("Using CPU device")

            # Set CPU-specific environment variables
            if 'cpu_kvcache_space' in launcher_config:
                os.environ['VLLM_CPU_KVCACHE_SPACE'] = str(launcher_config['cpu_kvcache_space'])
            if 'cpu_omp_threads_bind' in launcher_config:
                os.environ['VLLM_CPU_OMP_THREADS_BIND'] = str(launcher_config['cpu_omp_threads_bind'])
        else:
            # GPU configuration
            if isinstance(cuda_devices, str):
                cuda_devices = cuda_devices.split(',')
            os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(map(str, cuda_devices))
            print(f"Using CUDA devices: {os.environ['CUDA_VISIBLE_DEVICES']}")

            # Auto-set tensor parallel size based on number of devices
            if not args.tensor_parallel_size and 'tensor_parallel_size' not in vllm_config:
                vllm_config['tensor_parallel_size'] = len(cuda_devices)

    # Apply CLI overrides
    if args.port:
        vllm_config['port'] = args.port
    if args.tensor_parallel_size:
        vllm_config['tensor_parallel_size'] = args.tensor_parallel_size

    # Add any launcher config that should go to vLLM
    for key in ['gpu_memory_utilization']:
        if key in launcher_config:
            vllm_config[key] = launcher_config[key]

    # Create temporary clean config file for vLLM
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(vllm_config, f)
        temp_config = f.name

    try:
        # Build vLLM command
        cmd = ['vllm', 'serve', '--config', temp_config]

        # Add any additional unknown arguments
        cmd.extend(unknown_args)

        print(f"Launching vLLM with config: {vllm_config}")
        print(f"Command: {' '.join(cmd)}")

        # Launch vLLM
        if args.wait_for_ready or args.background:
            # Start vLLM in background and wait for it to be ready
            process = subprocess.Popen(cmd)
            port = vllm_config.get('port', 8000)

            print(f"Waiting for vLLM service on port {port} to be ready...")
            if wait_for_service_ready(port, args.timeout):
                print("✅ vLLM service is ready!")

                if args.background:
                    # Background mode: exit after ready, leave vLLM running
                    print(f"🚀 vLLM running in background with PID {process.pid}")
                    print("📝 Use 'kill {process.pid}' to stop the service")
                else:
                    # Wait-for-ready mode: keep process running in foreground
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        print("\n🛑 Shutting down vLLM service...")
                        process.terminate()
                        process.wait()
            else:
                print("❌ vLLM service failed to start or timed out")
                process.terminate()
                sys.exit(1)
        else:
            subprocess.run(cmd)

    finally:
        # Clean up temp file
        os.unlink(temp_config)


if __name__ == '__main__':
    main()