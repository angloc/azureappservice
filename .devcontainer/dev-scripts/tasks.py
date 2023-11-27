import os
import subprocess
from shlex import quote

from invoke import run as local
from invoke.tasks import task

def load_env_vars(file_path):
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = [x.strip() for x in line.split("=", 1)]
                value = value.strip("'\"")  # Removes quotes around values
                os.environ[key] = value
    except FileNotFoundError:
        print(f"{file_path} not found. Make sure you have a {file_path} file in the root of the project.")
        print("run dev-scripts/secrets.py to create one from a secrets vault")
        exit(1)


load_env_vars(".env")

WEB_SERVICE = os.getenv("WEB_SERVICE", "web")


def dexec(cmd, service=WEB_SERVICE):
    return local(
        "docker-compose exec -T {} bash -c {}".format(quote(service), quote(cmd)),
    )


def sudexec(cmd, service=WEB_SERVICE:
    return local(
        "docker-compose exec --user=root -T {} bash -c {}".format(quote(service), quote(cmd)),
    )


@task
def build(c):
    """
    Build the development environment (call this first)
    """
    local("docker-compose down -v --remove-orphans")
    local("docker-compose up --build --force-recreate")


@task
def start(c):
    """
    Start the development environment
    """
    local("docker-compose up")


@task
def stop(c):
    """
    Stop the development environment
    """
    local("docker-compose stop")


@task
def restart(c):
    """
    Restart the development environment
    """
    stop(c)
    start(c)


@task
def destroy(c):
    """
    Destroy development environment containers (database will lost!)
    """
    local("docker-compose down")


@task
def sh(c):
    """
    Run bash in the local web container
    """
    subprocess.run(["docker-compose", "exec", WEB_SERVICE, "bash"])


@task
def sh_root(c):
    """
    Run bash as root in the local web container
    """
    subprocess.run(["docker-compose", "exec", "--user=root", WEB_SERVICE, "bash"])


@task
def kill(c):
    """
    Kills all running docker contaners
    """
    local("docker container kill $(docker ps -q)")


@task
def qstart(c):
    """
    Quick start - kill, start and SH into the container
    """

    try:
        kill(c)
    except:  # noqa
        pass

    start(c)
    sh(c)

@task
def copy_file_out(ctx, input_path, output_path, service=None):

    """
    Copies a file or directory from a Docker container to the host.

    :param ctx: Context for invoke tasks.
    :param input_path: Path to the file or directory in the container.
    :param output_path: Path on the host to copy the file or directory to.
    :param service: Optional Docker Compose service name.
    """
    # Validate service parameter
    service = service or "web"
    if service:
        # Get the list of running containers for the service
        result = subprocess.run(
            ["docker-compose", "ps", "-q", service],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check for errors or no output
        if result.returncode != 0 or not result.stdout.strip():
            print(f"Error: There is no container running for the service '{service}'.")
            return

        container_ids = result.stdout.strip().split('\n')

        # Check if there are multiple containers
        if len(container_ids) > 1:
            print(f"Error: There are multiple containers running for the service '{service}'.")
            return

        container_id = container_ids[0]
    else:
        print("Error: Service name must be provided.")
        return

    # Check if input_path is a directory
    is_directory = input_path.endswith('/')

    # Construct docker cp command
    docker_cp_cmd = [
        "docker", "cp",
        f"{container_id}:{input_path}",
        output_path
    ]

    # Execute docker cp command
    result = subprocess.run(docker_cp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check for errors
    if result.returncode != 0:
        error_msg = result.stderr.decode().strip()
        if "not a directory" in error_msg and is_directory:
            print("Error: When copying directories, both input and output paths must be directories.")
        elif "No such file or directory" in error_msg:
            print("Error: The specified file or directory does not exist in the container.")
        else:
            print(f"Error: {error_msg}")
    else:
        print(f"Successfully copied {input_path} to {output_path}.")