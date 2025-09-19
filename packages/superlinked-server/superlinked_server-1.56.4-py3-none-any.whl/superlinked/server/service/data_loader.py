# Copyright 2024 Superlinked, Inc.
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

import asyncio
import logging
from collections.abc import Sequence

import pandas as pd
import structlog
from beartype.typing import Any
from pandas.io.json._json import JsonReader
from pandas.io.parsers import TextFileReader
from pydantic.alias_generators import to_snake

from superlinked.framework.common.telemetry.telemetry_registry import TelemetryAttributeType, telemetry
from superlinked.framework.dsl.source.data_loader_source import (
    DataFormat,
    DataLoaderConfig,
    DataLoaderSource,
)
from superlinked.server.exception.exception import DataLoaderNotFoundException

logger = structlog.getLogger(__name__)


class DataLoader:
    def __init__(self) -> None:
        self._data_loader_sources: dict[str, DataLoaderSource] = {}

    def register_data_loader_sources(self, data_loader_sources: Sequence[DataLoaderSource]) -> None:
        for source in data_loader_sources:
            if source.name in self._data_loader_sources:
                logger.warning(
                    "skipped registration",
                    reason="already registered",
                    source_name=source.name,
                )
                continue
            self._data_loader_sources[to_snake(source.name)] = source

    def get_data_loaders(self) -> dict[str, DataLoaderConfig]:
        return {name: source.config for name, source in self._data_loader_sources.items()}

    async def load(self, name: str) -> None:
        data_loader_source = self._data_loader_sources.get(name)
        if not data_loader_source:
            msg = f"Data loader with name: {name} not found"
            raise DataLoaderNotFoundException(msg)
        task = asyncio.create_task(self.__read_and_put_data(data_loader_source))
        task.add_done_callback(self._task_done_callback)
        logger.info(
            "started data load",
            configuration=data_loader_source.config,
            task_name=task.get_name(),
        )

    async def __read_and_put_data(self, source: DataLoaderSource) -> None:
        data = self.__read_data(source.config.path, source.config.format, source.config.pandas_read_kwargs)
        labels: dict[str, TelemetryAttributeType] = {
            "data_loader_name": source.name,
            "schema": source._schema._schema_name,
            "data_format": source.config.format.value,
            "chunked": False,
        }
        if isinstance(data, pd.DataFrame):
            self.__print_memory_usage(data)
            logger.debug("loaded data frame to memory", chunked=False, size=len(data))
            with telemetry.span("data_loader.put", attributes=labels):
                await source.put_async([data])
            telemetry.record_metric("ingested_items_with_data_loader_total", len(data), labels=labels)
        elif isinstance(data, TextFileReader | JsonReader):
            for chunk in data:
                self.__print_memory_usage(chunk)
                logger.debug("loaded data frame to memory", chunked=True, size=len(chunk))
                labels["chunked"] = True
                with telemetry.span("data_loader.put", attributes=labels):
                    await source.put_async([chunk])
                telemetry.record_metric("ingested_items_with_data_loader_total", len(chunk), labels=labels)
        else:
            error_message = (
                "The returned object from the Pandas read method was not of the "
                f"expected type. Actual type: {type(data)}"
            )
            raise TypeError(error_message)
        logger.info("finished data load", source_name=source.name)

    def _task_done_callback(self, task: asyncio.Task) -> None:
        try:
            task.result()
        except Exception:  # pylint: disable=broad-except
            logger.exception("failed task", task_name=task.get_name())

    def __read_data(
        self,
        path: str,
        data_format: DataFormat,
        pandas_read_kwargs: dict[str, Any] | None,
    ) -> pd.DataFrame | TextFileReader | JsonReader:
        kwargs = pandas_read_kwargs or {}
        match data_format:
            case DataFormat.CSV:
                return pd.read_csv(path, **kwargs)
            case DataFormat.FWF:
                return pd.read_fwf(path, **kwargs)
            case DataFormat.XML:
                return pd.read_xml(path, **kwargs)
            case DataFormat.JSON:
                return pd.read_json(path, **kwargs)
            case DataFormat.PARQUET:
                return pd.read_parquet(path, **kwargs)
            case DataFormat.ORC:
                return pd.read_orc(path, **kwargs)
            case _:
                msg = "Unsupported data format: %s"
                raise ValueError(msg, data_format)

    # TODO FAI-2328: This is printing not logging the data.
    def __print_memory_usage(self, df: pd.DataFrame) -> None:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            df.info(memory_usage=True)
