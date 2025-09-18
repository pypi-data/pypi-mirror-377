import argparse
from dataclasses import dataclass
from typing import Union, List


@dataclass(frozen=True)
class OutDataset:
    dataset: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str

    def __init__(self, *args, **kwargs):
        # prevent direct construction
        raise RuntimeError("Use OutDataset.from_cli() to create an instance")

    @classmethod
    def from_cli(cls, n: int = 1) -> Union[List["OutDataset"], "OutDataset"]:
        """Register arguments, parse CLI, and return immutable InDataset."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--output-dataset-{i}",
                    dest=f"output_dataset_{i}_dataset",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minio_bucket",
                    dest=f"output_dataset_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minIO_URL",
                    dest=f"output_dataset_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minIO_ACCESS_KEY",
                    dest=f"output_dataset_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minIO_SECRET_KEY",
                    dest=f"output_dataset_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args, _ = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    cls.__create_instance(
                        getattr(args, f"output_dataset_{i}_dataset"),
                        getattr(args, f"output_dataset_{i}_minio_bucket"),
                        getattr(args, f"output_dataset_{i}_minio_url"),
                        getattr(args, f"output_dataset_{i}_access_key"),
                        getattr(args, f"output_dataset_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--output-dataset", dest="output_dataset", type=str, required=True
            )
            parser.add_argument(
                "--output-dataset.minio_bucket",
                dest="output_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-dataset.minIO_URL",
                dest="output_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-dataset.minIO_ACCESS_KEY",
                dest="output_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-dataset.minIO_SECRET_KEY",
                dest="output_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return cls.__create_instance(
                dataset=args.output_dataset,
                bucket=args.output_minio_bucket,
                url=args.output_minio_url,
                access_key=args.output_access_key,
                secret_key=args.output_secret_key,
            )

    @staticmethod
    def __create_instance(dataset, bucket, url, access_key, secret_key):
        """Bypass __init__ and set attributes for a frozen dataclass."""
        obj = object.__new__(OutDataset)
        object.__setattr__(obj, "dataset", dataset)
        object.__setattr__(obj, "minio_bucket", bucket)
        object.__setattr__(obj, "minio_url", url)
        object.__setattr__(obj, "access_key", access_key)
        object.__setattr__(obj, "secret_key", secret_key)
        return obj


@dataclass(frozen=True)
class OutModel:
    model: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str

    def __init__(self, *args, **kwargs):
        # prevent direct construction
        raise RuntimeError("Use OutModel.from_cli() to create an instance")

    @classmethod
    def from_cli(cls, n: int = 1) -> Union[List["OutModel"], "OutModel"]:
        """Register arguments, parse CLI, and return immutable InModel."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--output-model-{i}",
                    dest=f"output_model_{i}",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minio_bucket",
                    dest=f"output_model_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minIO_URL",
                    dest=f"output_model_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minIO_ACCESS_KEY",
                    dest=f"output_model_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minIO_SECRET_KEY",
                    dest=f"output_model_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    cls.__create_instance(
                        getattr(args, f"output_model_{i}"),
                        getattr(args, f"output_model_{i}_minio_bucket"),
                        getattr(args, f"output_model_{i}_minio_url"),
                        getattr(args, f"output_model_{i}_access_key"),
                        getattr(args, f"output_model_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--output-model", dest="output_model", type=str, required=True
            )
            parser.add_argument(
                "--output-model.minio_bucket",
                dest="output_model_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-model.minIO_URL",
                dest="output_model_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-model.minIO_ACCESS_KEY",
                dest="output_model_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-model.minIO_SECRET_KEY",
                dest="output_model_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return cls.__create_instance(
                model=args.output_model,
                bucket=args.output_model_minio_bucket,
                url=args.output_model_minio_url,
                access_key=args.output_model_access_key,
                secret_key=args.output_model_secret_key,
            )

    @staticmethod
    def __create_instance(model, bucket, url, access_key, secret_key):
        """Bypass __init__ and set attributes for a frozen dataclass."""
        obj = object.__new__(OutModel)
        object.__setattr__(obj, "model", model)
        object.__setattr__(obj, "minio_bucket", bucket)
        object.__setattr__(obj, "minio_url", url)
        object.__setattr__(obj, "access_key", access_key)
        object.__setattr__(obj, "secret_key", secret_key)
        return obj
