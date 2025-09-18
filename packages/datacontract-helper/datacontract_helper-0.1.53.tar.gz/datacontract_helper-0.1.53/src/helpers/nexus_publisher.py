import logging
import os
import subprocess

log = logging.getLogger(name="").getChild(suffix=__name__)


class NexusPublisher:
    def publish_package(
        self,
        nexus_user: str,
        nexus_pass: str,
        nexus_repo: str,
        wheel_file: str,
    ):

        # upload_nexus: str = f"uv run twine upload --repository-url {nexus_repo} --username {nexus_user} --password {nexus_pass} {wheel_file}"
        # result: subprocess.CompletedProcess = subprocess.run(
        #     args=upload_nexus,
        #     shell=True,
        #     executable="/bin/bash",  # или '/bin/zsh'
        #     capture_output=True,
        #     text=True,
        #     check=True,
        # )

        env: dict = os.environ.copy()
        # Добавляем учетные данные в переменные окружения
        env["TWINE_USERNAME"] = nexus_user
        env["TWINE_PASSWORD"] = nexus_pass
        env["TWINE_REPOSITORY_URL"] = nexus_repo

        result: subprocess.CompletedProcess = subprocess.run(
            args=[
                "uv",
                "run",
                "twine",
                "upload",
                # "--repository-url", nexus_repo,
                # "--username", nexus_user,
                # "--password", nexus_pass,
                wheel_file,
            ],
            env=env,
            shell=False,
            capture_output=True,
            text=True,
            check=True,
        )
