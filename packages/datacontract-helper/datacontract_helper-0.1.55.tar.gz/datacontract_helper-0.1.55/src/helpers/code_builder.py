import logging
import subprocess

import click
from datacontract.data_contract import DataContract
from grpc_tools import protoc



log = logging.getLogger(name="").getChild(suffix=__name__)


class ModuleBuilder:

    def create_yaml_from_sql(self, filename: str = "test"):

        # create_yaml: str = (
        #     f"""uv run datacontract import --format sql --source {filename}.sql --output {filename}.yaml"""
        # )
        # click.echo(message=create_yaml)

        # result: subprocess.CompletedProcess = subprocess.run(
        #     args=create_yaml,
        #     shell=True,
        #     executable="/bin/bash",  # или '/bin/zsh'
        #     capture_output=True,
        #     text=True,
        #     check=True,
        # )

        result: subprocess.CompletedProcess = subprocess.run(
            args=[
                "uv", "run", "datacontract", "import",
                "--format", "sql",
                "--source", f"{filename}.sql",
                "--output", f"{filename}.yaml"
                ],
            shell=False,
            capture_output=True,
            text=True,
            check=True,
        )

        click.echo(message=result)



    def create_proto_from_yaml(self, filename: str = "vertica_datacontract"):
        """нужен файлик your-datacontract.yaml"""

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        file_to_create: str = f"{filename}.proto"

        with open(file=file_to_create, mode="wb") as f:
            f.write(data_contract.export(export_format="protobuf")["protobuf"].encode())

        click.echo(message=f"created file: {file_to_create}")


    def generate_python_code_from_proto(self, filename: str):
        # TODO: мне кажется здесь надо принимать не название .proto файла, а сам файл в качестве аргумента

        protoc.main(["protoc", "--python_out=.", f"{filename}.proto"])
        click.echo(message=f"created file {filename}_pb2.py")
