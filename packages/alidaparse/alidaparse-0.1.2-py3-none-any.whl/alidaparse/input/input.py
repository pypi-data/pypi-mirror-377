import argparse
from dataclasses import dataclass
from typing import Union, List, Any


@dataclass(frozen=True)
class InParam:
    param_value: str
    param_name: str

    def __init__(self, *args, **kwargs):
        # prevent direct construction
        raise RuntimeError("Use InParam.from_cli() to create an instance")

    @classmethod
    def from_cli(
        cls, name: str, required: bool, n: int = 1
    ) -> Union[List["InParam"], "InParam"]:
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--{name}-{i}", dest=f"{name}_{i}", required=required, type=str
                )
            args = parser.parse_args()
            for i in range(1, n + 1):
                objs.append(
                    cls.__create_instance(
                        f"{name}_{i}",
                        getattr(args, f"{name}_{i}"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                f"--{name}", dest=f"{name}", required=required, type=str
            )
            args = parser.parse_args()
            return cls.__create_instance(f"{name}", getattr(args, f"{name}"))

    @staticmethod
    def __create_instance(param_name, param_value):
        """Bypass __init__ and set attributes for a frozen dataclass."""
        obj = object.__new__(InParam)
        object.__setattr__(obj, "param_name", param_name)
        object.__setattr__(obj, "param_value", param_value)
        return obj


@dataclass(frozen=True)
class InDataset:
    dataset: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str

    def __init__(self, *args, **kwargs):
        # prevent direct construction
        raise RuntimeError("Use InDataset.from_cli() to create an instance")

    @classmethod
    def from_cli(cls, n: int = 1) -> Union[List["InDataset"], "InDataset"]:
        """Register arguments, parse CLI, and return immutable InDataset."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--input-dataset-{i}",
                    dest=f"input_dataset_{i}",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minio_bucket",
                    dest=f"input_dataset_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minIO_URL",
                    dest=f"input_dataset_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minIO_ACCESS_KEY",
                    dest=f"input_dataset_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minIO_SECRET_KEY",
                    dest=f"input_dataset_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args, _ = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    cls.__create_instance(
                        getattr(args, f"input_dataset_{i}"),
                        getattr(args, f"input_dataset_{i}_minio_bucket"),
                        getattr(args, f"input_dataset_{i}_minio_url"),
                        getattr(args, f"input_dataset_{i}_access_key"),
                        getattr(args, f"input_dataset_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--input-dataset", dest="input_dataset", type=str, required=True
            )
            parser.add_argument(
                "--input-dataset.minio_bucket",
                dest="input_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-dataset.minIO_URL",
                dest="input_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-dataset.minIO_ACCESS_KEY",
                dest="input_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-dataset.minIO_SECRET_KEY",
                dest="input_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return cls.__create_instance(
                dataset=args.input_dataset,
                bucket=args.input_minio_bucket,
                url=args.input_minio_url,
                access_key=args.input_access_key,
                secret_key=args.input_secret_key,
            )

    @staticmethod
    def __create_instance(dataset, bucket, url, access_key, secret_key):
        """Bypass __init__ and set attributes for a frozen dataclass."""
        obj = object.__new__(InDataset)
        object.__setattr__(obj, "dataset", dataset)
        object.__setattr__(obj, "minio_bucket", bucket)
        object.__setattr__(obj, "minio_url", url)
        object.__setattr__(obj, "access_key", access_key)
        object.__setattr__(obj, "secret_key", secret_key)
        return obj


@dataclass(frozen=True)
class InModel:
    model: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str

    def __init__(self, *args, **kwargs):
        # prevent direct construction
        raise RuntimeError("Use InModel.from_cli() to create an instance")

    @classmethod
    def from_cli(cls, n: int = 1) -> Union[List["InModel"], "InModel"]:
        """Register arguments, parse CLI, and return immutable InModel."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--input-model-{i}",
                    dest=f"input_model_{i}",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minio_bucket",
                    dest=f"input_model_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minIO_URL",
                    dest=f"input_model_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minIO_ACCESS_KEY",
                    dest=f"input_model_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minIO_SECRET_KEY",
                    dest=f"input_model_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args, _ = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    cls.__create_instance(
                        getattr(args, f"input_model_{i}"),
                        getattr(args, f"input_model_{i}_minio_bucket"),
                        getattr(args, f"input_model_{i}_minio_url"),
                        getattr(args, f"input_model_{i}_access_key"),
                        getattr(args, f"input_model_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--input-model", dest="input_model", type=str, required=True
            )
            parser.add_argument(
                "--input-model.minio_bucket",
                dest="input_model_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-model.minIO_URL",
                dest="input_model_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-model.minIO_ACCESS_KEY",
                dest="input_model_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-model.minIO_SECRET_KEY",
                dest="input_model_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return cls.__create_instance(
                model=args.input_model,
                bucket=args.input_model_minio_bucket,
                url=args.input_model_minio_url,
                access_key=args.input_model_access_key,
                secret_key=args.input_model_secret_key,
            )

    @staticmethod
    def __create_instance(model, bucket, url, access_key, secret_key):
        """Bypass __init__ and set attributes for a frozen dataclass."""
        obj = object.__new__(InModel)
        object.__setattr__(obj, "model", model)
        object.__setattr__(obj, "minio_bucket", bucket)
        object.__setattr__(obj, "minio_url", url)
        object.__setattr__(obj, "access_key", access_key)
        object.__setattr__(obj, "secret_key", secret_key)
        return obj
