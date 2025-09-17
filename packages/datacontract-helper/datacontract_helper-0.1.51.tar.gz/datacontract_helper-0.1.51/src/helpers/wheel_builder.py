import logging
import os
import shutil
import subprocess
import tempfile
from datacontract.data_contract import DataContract
import click

# NEXUS_URL: str = os.environ["NEXUS_URL"]
# NEXUS_USERNAME: str = os.environ["NEXUS_USERNAME"]
# NEXUS_PASSWORD: str = os.environ["NEXUS_PASSWORD"]


log = logging.getLogger(name="").getChild(suffix=__name__)


SEND_TO_KAFKA_TXT: str = """

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from google.protobuf.message import Message

class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str = broker,
        schema_registry_url: str = schema_registry,
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


class WheelBuilder:

    def __init__(self): ...

    def build_wheel(
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
                    f.write(
                        "\n".join(
                            f'{key} = "{value}"'
                            for key, value in self.get_urls(filename=filename).items()
                        )
                    )
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
        # run = data_contract.test()
        # if not run.has_passed():
        #     raise Exception("Data quality validation failed.")
        # kafka://
        
        return {key: value.replace("kafka://", "") if key == "broker" else value for key, value in data_contract.get_data_contract_specification().links.items()}
        # data_contract.get_data_contract_specification().links["schema_registry"]
        # data_contract.get_data_contract_specification().links["broker"]
