#!/usr/bin/env python3

import argparse
import paramiko
import os

def ssh_connect(host, username, key_filename):
    # Create an SSH client using key-based authentication
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the host using SSH
        client.connect(hostname=host, username=username, key_filename=key_filename)
        return client

    except (paramiko.AuthenticationException, paramiko.SSHException) as e:
        print(f"Failed to connect to {host}: {str(e)}")
        return None

def get_disk_usage(client, location):
    stdin, stdout, stderr = client.exec_command(f"df -h {location} | awk 'NR==2 {{print $5}}'")
    disk_usage = stdout.read().decode('utf-8').strip()
    return disk_usage

def get_cpu_usage(client):
    stdin, stdout, stderr = client.exec_command(f"top -bn1 | grep 'Cpu(s)' | awk '{{print $2 + $4}}'")
    cpu_usage = stdout.read().decode('utf-8').strip()
    return cpu_usage

def get_mem_usage(client):
    stdin, stdout, stderr = client.exec_command(f"free | awk 'FNR == 2 {{print $3/$2 * 100}}'")
    mem_usage = stdout.read().decode('utf-8').strip()
    return mem_usage

def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("ip_address", help="IP address of the server to monitor")
    parser.add_argument("disk_root", help="Disk Root")
    parser.add_argument("disk_app", help="Disk App")
    args = parser.parse_args()
    server_ip = args.ip_address
    root_disk = args.disk_root
    app_disk = args.disk_app

    # SSH details
    #hosts = ['10.16.51.15', '10.16.51.6', '10.16.50.241', '10.16.51.192']
    private_key = os.path.expanduser('/.ssh/id_rsa')
    username = "app"
    #key_filename = private_key

    # Connect to the server
    client = ssh_connect(server_ip, username, private_key)

    if client:
        try:
            # Get CPU usage
            cpu_usage = get_cpu_usage(client)
            # Get Memory usage
            mem_usage = get_mem_usage(client)
            # Get Disk usage for root directory '/'
            disk_usage_root = get_disk_usage(client, root_disk)
            # Get Disk usage for '/app' directory
            disk_usage_app = get_disk_usage(client, app_disk)

            # Print results
            print(f'Host: {server_ip}')
            print(f'CPU_usage: {cpu_usage}%')
            print(f'Memory_usage: {mem_usage}%')
            print(f'Disk_usage_root: {disk_usage_root}')
            print(f'Disk_usage_app: {disk_usage_app}')
        finally:
            # Close the SSH connection
            client.close()
    else:
        print("SSH connection failed.")

if __name__ == "__main__":
    main()