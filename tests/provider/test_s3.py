"""Модуль для тестов S3Provider: загрузка, чтение, удаление, листинг."""

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from hamcrest import assert_that, contains_inanyorder, equal_to
from hamcrest.core.matcher import Matcher

from tests.provider.helpers import BytesBody, aiter_pages
from weblite_framework.provider.s3 import S3Provider


class TestS3Provider:
    """Набор юнит-тестов для S3Provider."""

    async def test_upload_file_calls_put_object(
        self,
        provider: S3Provider,
        s3_client: AsyncMock,
    ) -> None:
        """Проверяет вызов put_object у upload_file.

        Args:
            provider: S3Provider.
            s3_client: Мокнутый S3 client.
        """
        await provider.upload_file(filename='docs/a.txt', data=b'DATA')

        s3_client.put_object.assert_awaited_once()
        kwargs = s3_client.put_object.await_args.kwargs
        assert_that(kwargs['Bucket'], equal_to(provider.settings.bucket))
        assert_that(kwargs['Key'], equal_to('docs/a.txt'))
        assert_that(kwargs['Body'], equal_to(b'DATA'))

    async def test_get_file_returns_bytes(
        self,
        provider: S3Provider,
        s3_client: AsyncMock,
    ) -> None:
        """Проверяет возврат содержимого объекта методом get_file.

        Args:
            provider: S3Provider.
            s3_client: Мокнутый S3 client.
        """
        s3_client.get_object = AsyncMock(
            return_value={'Body': BytesBody(data=b'hello')},
        )

        data = await provider.get_file(filename='file.bin')
        s3_client.get_object.assert_awaited_once()
        kwargs = s3_client.get_object.await_args.kwargs

        assert_that(data, equal_to(b'hello'))
        assert_that(kwargs['Bucket'], equal_to(provider.settings.bucket))
        assert_that(kwargs['Key'], equal_to('file.bin'))

    async def test_delete_file_calls_delete_object(
        self,
        provider: S3Provider,
        s3_client: AsyncMock,
    ) -> None:
        """Проверяет вызов delete_object у метода delete_file.

        Args:
            provider: S3Provider.
            s3_client: Мокнутый S3 client.
        """
        await provider.delete_file(filename='to_remove.txt')

        s3_client.delete_object.assert_awaited_once()
        kwargs = s3_client.delete_object.await_args.kwargs
        assert_that(kwargs['Bucket'], equal_to(provider.settings.bucket))
        assert_that(kwargs['Key'], equal_to('to_remove.txt'))

    async def test_get_files_list_merges_pages(
        self,
        provider: S3Provider,
        s3_client: AsyncMock,
    ) -> None:
        """Проверяет сбор ключей со всех страниц методом get_files_list.

        Args:
            provider: S3Provider.
            s3_client: Мокнутый S3 client.
        """
        paginator = MagicMock()
        s3_client.get_paginator = MagicMock(return_value=paginator)

        pages = [
            {'Contents': [{'Key': 'x/a.txt'}, {'Key': 'x/b.txt'}]},
            {'Contents': [{'Key': 'x/c.txt'}]},
        ]
        paginator.paginate.return_value = aiter_pages(pages=pages)

        keys = await provider.get_files_list(prefix='x/')
        s3_client.get_paginator.assert_called_once_with(
            operation_name='list_objects_v2',
        )
        paginator.paginate.assert_called_once_with(
            Bucket=provider.settings.bucket,
            Prefix='x/',
        )
        matcher = cast(
            Matcher[list[str]],
            contains_inanyorder(
                'x/a.txt',
                'x/b.txt',
                'x/c.txt',
            ),
        )
        assert_that(
            actual_or_assertion=list(keys),
            matcher=matcher,
        )

    @pytest.mark.parametrize(
        argnames=('method', 'args'),
        argvalues=[
            ('upload_file', {'filename': '', 'data': b'data'}),
            ('get_file', {'filename': ''}),
            ('delete_file', {'filename': ''}),
        ],
    )
    async def test_validate_filename_raises(
        self,
        provider: S3Provider,
        method: str,
        args: dict[str, Any],
    ) -> None:
        """Проверяет вызов ValueError при пустом имени файла.

        Args:
            provider: S3Provider.
            method: Имя тестируемого метода.
            args: Аргументы для вызова метода.
        """
        with pytest.raises(expected_exception=ValueError):
            await getattr(provider, method)(**args)

    async def test_upload_file_requires_data(
        self, provider: S3Provider
    ) -> None:
        """Проверяет вызов ValueError при отсутствии аргумента data.

        Args:
            provider: S3Provider.
        """
        with pytest.raises(expected_exception=ValueError):
            await provider.upload_file(
                filename='ok.txt',
                data=cast(bytes, None),
            )
