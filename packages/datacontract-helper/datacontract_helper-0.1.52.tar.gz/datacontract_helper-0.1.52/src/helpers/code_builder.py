import json
import logging
import os
import shutil
import subprocess
import tempfile

import click
import requests
from confluent_kafka import Consumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from datacontract.data_contract import DataContract
from google.protobuf.message import Message
from grpc_tools import protoc
# from person_pb2 import Person
from requests.auth import HTTPBasicAuth
from twine.commands.upload import upload






log = logging.getLogger(name="").getChild(suffix=__name__)

topic: str = "test"
def send_to_kafka(
    self,
    proto_message: Message,
    topic: str = topic,
    key=None):
    """сама по себе эта функция не нужна, нужен ее клон SEND_TO_KAFKA_TXT"""

    protobuf_serializer: ProtobufSerializer = ProtobufSerializer(
        msg_type=proto_message.__class__,
        schema_registry_client=SchemaRegistryClient(
            conf={"url": f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}"}
        ),
    )

    producer: Producer = Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "python-producer",
        }
    )

    value = protobuf_serializer(
        message=proto_message,
        ctx=SerializationContext(topic=topic, field=MessageField.VALUE),
    )

    producer.produce(
        topic=topic,
        # key=key,
        value=value,
    )
    producer.flush()



SEND_TO_KAFKA_TXT: str = """

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from google.protobuf.message import Message

class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str = broker, # should be imported from .yml
        schema_registry_url: str = schema_registry, # should be imported from .yml
        client_id: str = "datacontract-python-producer",
    ):
        self.producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "client.id": client_id,
            }
        )

        self.schema_registry_client = SchemaRegistryClient(
            conf={"url": schema_registry_url}
        )
        self.serializers_cache = {}

    def _get_serializer(self, proto_message_type):
        if proto_message_type not in self.serializers_cache:
            self.serializers_cache[proto_message_type] = ProtobufSerializer(
                msg_type=proto_message_type,
                schema_registry_client=self.schema_registry_client,
            )
        return self.serializers_cache[proto_message_type]

    def send_to_kafka(
        self,
        proto_message: Message,
        topic: str = topic,
        key=None):
        serializer = self._get_serializer(proto_message.__class__)

        value = serializer(
            message=proto_message,
            ctx=SerializationContext(topic=topic, field=MessageField.VALUE),
        )
        

        self.producer.produce(
            topic=topic,
            key=key,
            value=value,
        )

    def flush(self, timeout=5.0):
        self.producer.flush(timeout=timeout)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()



"""


class ModuleBuilder:

    def __init__(self): ...

    def create_wheel(
        self,
        proto_file_name: str = "vertica_datacontract_pb2",
        filename: str = "vertica_datacontract",
        version: str = "0.1.8",
    ):
        module_folder = filename 

        # VERSION: str = "0.1.8"

        # MODULE_NAME: str = "vertica-datacontract-tool"
        # MODULE_NAME: str = "vertica_datacontract_tool"

        # у нас должен быть файл proto.py:
        # PROTO_FILE_NAME: str = "vertica_datacontract_pb2"

        # MODULE_FOLDER: str = "vertica_datacontract"

        # pyproject_toml_content: str = """
        # [build-system]
        # requires = ["setuptools", "wheel"]
        # build-backend = "setuptools.build_meta"
        # """

        setup_file_content: str = f"""
from setuptools import setup, find_packages

setup(
    name="{module_folder}",
    version="{version}",# my_package.__version__,
    # author=my_package.__author__,
    packages=find_packages(),
    install_requires=[
        "protobuf>=3.20.0",
        "build>=1.3.0",
        "confluent-kafka[all]>=2.11.1",
        "pip>=25.2",
        ],

)
"""

        with tempfile.TemporaryDirectory() as tmpdirname:
            setup_file: str = os.path.join(tmpdirname, "setup.py")

            with open(setup_file, "w") as f:
                f.write(setup_file_content)

            module_folder_path: str = os.path.join(tmpdirname, module_folder)
            os.makedirs(module_folder_path)  # , exist_ok=True)

            init_file: str = os.path.join(module_folder_path, "__init__.py")

            with open(f"{proto_file_name}.py", "r") as proto1:
                with open(init_file, "w") as f:
                    f.write(proto1.read())
                    f.write("\n\n")


                    f.write("\n".join(self.get_tags(filename=filename)))
                    f.write("\n\n")
                    f.write("\n".join(f"{key} = \"{value}\"" for key, value in self.get_urls(filename=filename).items()))
                    f.write("\n\n")


                    f.write(SEND_TO_KAFKA_TXT)

            with open(init_file, "r") as f:
                click.echo("its __init__.py")
                click.echo(f.read())
            with open(setup_file, "r") as f:
                click.echo("its setup.py")
                click.echo(f.read())

            subprocess.run(
                args=["python", "setup.py", "bdist_wheel"],
                check=True,
                cwd=tmpdirname,  # указать working directory
            )

            dist_folder: str = os.path.join(tmpdirname, "dist")
            wheels: list[str] = [
                os.path.join(dist_folder, filepath)
                for filepath in os.listdir(dist_folder)
            ]
            click.echo({"wheels": wheels})

            for wheel in wheels:
                subprocess.run(
                    args=["python", "-m", "pip", "install", wheel],
                    check=True,
                    cwd=tmpdirname,  # указать working directory
                )

            real_dir = os.getcwd()
            for wheel in wheels:
                click.echo(f"try copy2 {wheel}")
                shutil.copy2(src=wheel, dst=real_dir)

    def publish_package(
        self,
        nexus_user: str,
        nexus_pass: str,
        nexus_repo: str,
        wheel_file: str,
    ):

        upload_nexus: str = f"uv run twine upload --repository-url {nexus_repo} --username {nexus_user} --password {nexus_pass} {wheel_file}"
        # click.echo(message=upload_nexus)
        result: subprocess.CompletedProcess = subprocess.run(
            args=upload_nexus,
            shell=True,
            executable="/bin/bash",  # или '/bin/zsh'
            capture_output=True,
            text=True,
            check=True,
        )
        # click.echo(message="\n\n")
        # click.echo(message=result)

        # with open(file=file_path, mode="rb") as file:

        #     response: requests.Response = requests.put(
        #         url=f"{nexus_url}/repository/{nexus_repo_path}/{os.path.basename(p=file_path)}",
        #         auth=HTTPBasicAuth(username=username, password=password),
        #         data=file,
        #         headers={"Content-Type": "application/json"},
        #         timeout=20,
        #     )
        #     response.raise_for_status()
        #     click.echo(
        #         message=f"The file has been successfully uploaded to Nexus: {response.url}"
        #     )

    def validate_custom(self, filename: str):
        """удалить не нужен"""

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()
        # run = data_contract.test()
        # if not run.has_passed():
        #     raise Exception("Data quality validation failed.")
        #     # Abort pipeline, alert, or take corrective actions...


        click.echo(message=f" hello is custom validate {filename}.yaml")

    def create_yaml_from_sql(self, filename: str = "test"):
        # TODO: может можно как-то питоновским кодом сделать, без subprocess

        create_yaml: str = (
            f"""uv run datacontract import --format sql --source {filename}.sql --output {filename}.yaml"""
        )
        click.echo(message=create_yaml)

        result: subprocess.CompletedProcess = subprocess.run(
            args=create_yaml,
            shell=True,
            executable="/bin/bash",  # или '/bin/zsh'
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

    def publish_schema_registry(
        self,
        filename: str,
        subject_name: str = "vertica_datacontract",
    ):

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()
        # run = data_contract.test()
        # if not run.has_passed():
        #     raise Exception("Data quality validation failed.")
        #     # Abort pipeline, alert, or take corrective actions...
        click.echo(message=data_contract.export(export_format="avro"))
        schema_registry: str = data_contract.get_data_contract_specification().links["schema_registry"]
        # Запрос на регистрацию схемы
        response: requests.Response = requests.post(
            url=f"{schema_registry}/subjects/{subject_name}/versions",
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            json={
                "schemaType": "PROTOBUF",
                "schema": data_contract.export(export_format="protobuf")["protobuf"],
            },
            timeout=200,
        )
        click.echo(message=response.url)
        click.echo(message=response.text)
        click.echo(message=response.status_code)

    def get_tags(self, filename: str) -> list[str]:
        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        return data_contract.get_data_contract_specification().tags

    def get_urls(self, filename: str) -> dict:
        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        
        return {key: value.replace("kafka://", "") if key == "broker" else value for key, value in data_contract.get_data_contract_specification().links.items()}
        # data_contract.get_data_contract_specification().links["schema_registry"]
        # data_contract.get_data_contract_specification().links["broker"]


    def validate_schema_registry(
        self,
        subject_name: str,
        filename: str,
        version: str = "latest",
        compatibility_type: str = "FULL",
    ):
        """переименовать в validate"""
        # CompatibilityType = Literal["NONE", "FULL", "FORWARD", "BACKWARD", "FULL_TRANSITIVE"]

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()
        # run = data_contract.test()
        # if not run.has_passed():
        #     raise Exception("Data quality validation failed.")
        #     # Abort pipeline, alert, or take corrective actions...

        schema_registry: str = data_contract.get_data_contract_specification().links["schema_registry"]
        #   broker: ht
        response: requests.Response = requests.post(
            url=f"{schema_registry}/compatibility/subjects/{subject_name}/versions/{version}",
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            data=json.dumps(
                obj={
                    "schema": data_contract.export(export_format="protobuf")[
                        "protobuf"
                    ],
                    "schemaType": "PROTOBUF",
                    "compatibility": compatibility_type,
                }
            ),
            timeout=20,
        )
        click.echo(message=response.text)



