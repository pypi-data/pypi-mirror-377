# ************************************************************************
# Copyright 2025 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ************************************************************************
"""Module allows to use AWS SSM"""

# --------------------------------
#
# --------------------------------
import logging
import os
import pprint
import random
import string
import tempfile
import time

from o7cli.base import Base

logger = logging.getLogger(__name__)


def generate_password(length=16):
    """Generate a random password with at least one number, lowercase, uppercase, and special char"""
    if length < 4:
        raise ValueError("Password length must be at least 4")

    chars = [
        random.choice(string.ascii_lowercase),  # noqa: S311
        random.choice(string.ascii_uppercase),  # noqa: S311
        random.choice(string.digits),  # noqa: S311
        random.choice("!@#$%^&*()-_=+[]{};,.<>?"),  # noqa: S311
    ]
    chars += random.choices(  # noqa: S311
        string.ascii_letters + string.digits + "!#$%&*()-_=+[]{}|;:,.<>?",
        k=length - 4,
    )
    random.shuffle(chars)  # noqa: S311
    return "".join(chars)


# *************************************************
#
# *************************************************
class Ssm(Base):
    """Class for SSM Parameter Store"""

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html

    # *************************************************
    #
    # *************************************************
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = self.session.client("ssm")

        self.sessions = None

    # *************************************************
    #
    # *************************************************
    def load_sessions(self):
        """Load all sessions in Region"""

        logger.info("load_sessions")

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html
        paginator = self.client.get_paginator("describe_sessions")
        self.sessions = []
        param = {
            "State": "Active",  # Only load active sessions
        }

        for page in paginator.paginate(**param):
            self.sessions.extend(page.get("Instances", []))

        logger.info(f"load_sessions: Number of Sessions found {len(self.sessions)}")

        return self

    # *************************************************
    #
    # *************************************************
    def run_remote_powershell(self, instance_id, script):
        """Run a remote script on an instance using SSM"""
        logger.info(f"Running Remote Script on {instance_id}")

        resp = self.client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunPowerShellScript",
            Parameters={"commands": [script]},
            Comment="Running script via SSM",
        )

        command_id = resp["Command"]["CommandId"]
        logger.info(f"Running command with ID: {command_id}")

        # Wait for the command to complete
        waiter = self.client.get_waiter("command_executed")
        try:
            waiter.wait(
                CommandId=command_id,
                InstanceId=instance_id,
                WaiterConfig={"Delay": 5, "MaxAttempts": 60},
            )
        except Exception as e:
            logger.error(f"Error waiting for command execution: {e}")

        # Check the command status
        resp = self.client.list_command_invocations(CommandId=command_id, Details=True)
        status = resp["CommandInvocations"][0]["Status"]
        output = resp["CommandInvocations"][0]["CommandPlugins"][0]["Output"]

        print(f"Command Status: {status}")
        print("--------- Command Output ---------")
        print(output)
        print("----------------------------------")

        # Return the command output
        return status == "Success"

    # *************************************************
    #
    # *************************************************
    def start_port_forwarding_session(self, instance_id, port: int, local_port: int):
        """Start  a port forwarding session to an instance using SSM"""
        print(
            f"Starting session with {instance_id}, port {port}, local port {local_port}"
        )

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/start_session.html
        response = self.client.start_session(
            Target=instance_id,
            DocumentName="AWS-StartPortForwardingSession",
            Parameters={"portNumber": [str(port)], "localPortNumber": [str(local_port)]},
        )

        # print(response)
        session_id = response["SessionId"]
        print(f"Port Forwarding Session started with ID: {session_id}")

        return session_id

    # *************************************************
    #
    # *************************************************
    def rdp_set_user(self, user: str, instance_id: str):
        """Set the user for RDP connection"""

        password = generate_password(32)

        print(f"RDP User: {user}")
        print(f"RDP Password: {password}")

        # Define Script to set up RDP User
        rdp_set_user_script = f"""
    if (-not (Get-LocalUser -Name {user} -ErrorAction SilentlyContinue)) {{
        Write-Host "Create New RDP User"
        New-LocalUser -Name {user} -Password (ConvertTo-SecureString -AsPlainText "{password}" -Force) -FullName "RDP User" -Description "User for RDP access"
        Add-LocalGroupMember -Group "Remote Desktop Users" -Member {user}
        Add-LocalGroupMember -Group "Administrators" -Member {user}

        Add-LocalGroupMember -Group "Utilisateurs du Bureau à distance" -Member {user}
        Add-LocalGroupMember -Group "Administrateurs" -Member {user}
    }} else {{
        Write-Host "Setting New Password on existing RDP User"
        Set-LocalUser -Name {user} -Password (ConvertTo-SecureString -AsPlainText "{password}" -Force)
    }}
    Get-LocalUser
    """
        passed = self.run_remote_powershell(instance_id, rdp_set_user_script)

        return password if passed else None

    # *************************************************
    #
    # *************************************************
    def open_rdp_session(self, instance_id):
        """Open a remote desktop session to an instance using SSM"""
        logger.info(f"Opening RDP session with {instance_id}")

        port = 3389  # Default RDP port
        local_port = 13389  # Local port to forward to
        user = "RDPUserAuto"

        # Set the RDP user
        password = self.rdp_set_user(user=user, instance_id=instance_id)
        if password is None:
            print("Failed to set RDP User")
            return None

        session_id = self.start_port_forwarding_session(instance_id, port, local_port)

        print("Waiting 5 seconds for port forwarding session to establish...")
        time.sleep(5)

        self.load_sessions()
        pprint.pprint(self.sessions)

        # Prepare the RDP file content
        rdp_content = f"""full address:s:localhost:{local_port}
        username:s:{user}
        domain:s:
        """
        # Save the RDP file to a temporary location
        temp_dir = tempfile.gettempdir()
        rdp_file_path = os.path.join(temp_dir, "rdp_connection.rdp")
        with open(rdp_file_path, "w", encoding="ascii") as f:
            f.write(rdp_content)

        # Launch mstsc.exe with the RDP file
        print(f"Launching RDP connection: {rdp_file_path}")
        # subprocess.Popen(["mstsc.exe", rdp_file_path])

        print("")
        print(f"Please enter the password  when prompted -> {password} <-")

        return session_id


# *************************************************
#
# *************************************************
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    script = "Get-Process | Select-Object -First 5 | Format-Table -AutoSize"
    instance_id = "i-09072ec946e73d3bb"  # Replace with your

    the_obj = Ssm()
    # the_obj.run_remote_powershell(instance_id, script)
    the_obj.open_rdp_session(instance_id)

    # the_obj.start_port_forwarding_session(instance_id)

    # .menu_parameters()
