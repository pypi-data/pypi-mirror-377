import asyncio
import pytest
from btch_downloader import ttdl

@pytest.mark.asyncio
async def test_ttdl():
    result = await ttdl("https://vt.tiktok.com/ZSBnSFTeK/")
    assert "developer" in result
    assert result["developer"] == "@prm2.0"
