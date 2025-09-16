# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hfpy import HuggingFace, AsyncHuggingFace

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPosts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: HuggingFace) -> None:
        post = client.api.posts.delete(
            post_slug="postSlug",
            username="username",
        )
        assert post is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: HuggingFace) -> None:
        response = client.api.posts.with_raw_response.delete(
            post_slug="postSlug",
            username="username",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        post = response.parse()
        assert post is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: HuggingFace) -> None:
        with client.api.posts.with_streaming_response.delete(
            post_slug="postSlug",
            username="username",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            post = response.parse()
            assert post is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: HuggingFace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `username` but received ''"):
            client.api.posts.with_raw_response.delete(
                post_slug="postSlug",
                username="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `post_slug` but received ''"):
            client.api.posts.with_raw_response.delete(
                post_slug="",
                username="username",
            )


class TestAsyncPosts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncHuggingFace) -> None:
        post = await async_client.api.posts.delete(
            post_slug="postSlug",
            username="username",
        )
        assert post is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncHuggingFace) -> None:
        response = await async_client.api.posts.with_raw_response.delete(
            post_slug="postSlug",
            username="username",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        post = await response.parse()
        assert post is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncHuggingFace) -> None:
        async with async_client.api.posts.with_streaming_response.delete(
            post_slug="postSlug",
            username="username",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            post = await response.parse()
            assert post is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncHuggingFace) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `username` but received ''"):
            await async_client.api.posts.with_raw_response.delete(
                post_slug="postSlug",
                username="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `post_slug` but received ''"):
            await async_client.api.posts.with_raw_response.delete(
                post_slug="",
                username="username",
            )
