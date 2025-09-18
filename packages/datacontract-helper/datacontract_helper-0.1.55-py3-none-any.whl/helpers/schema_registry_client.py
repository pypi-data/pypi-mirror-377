import json
import logging

import click
import requests
from datacontract.data_contract import DataContract

log = logging.getLogger(name="").getChild(suffix=__name__)


class SchemaRegistryClient:
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
        schema_registry: str = data_contract.get_data_contract_specification().links[
            "schema_registry"
        ]
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

    def validate_schema_registry(
        self,
        subject_name: str,
        filename: str,
        version: str = "latest",
        # compatibility_type: str = "FULL",
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

        schema_registry: str = data_contract.get_data_contract_specification().links[
            "schema_registry"
        ]
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
                    # "compatibility": compatibility_type,
                }
            ),
            timeout=20,
        )
        click.echo(message=response.text)
