import json

import pytest

from kronik import PROJECT_ROOT
from kronik.brain.tiktok import analyze_tiktok
from kronik.models import Analysis, Category


@pytest.fixture
def test_paths():
    tiktok_fp = PROJECT_ROOT.joinpath("tests", "data", "tiktok-1.mp4")
    output_fp = tiktok_fp.with_suffix(".analysis.json")
    return tiktok_fp, output_fp


@pytest.mark.asyncio
async def test_analyze_tiktok_success(test_paths):
    tiktok_fp, output_fp = test_paths

    # Check if test file exists
    assert tiktok_fp.exists(), f"Test file not found: {tiktok_fp}"

    # Run analysis
    result = await analyze_tiktok(tiktok_fp)

    # Check that we got a result
    assert result is not None
    assert isinstance(result, Analysis)

    # Validate the structure of the response
    assert isinstance(result.transcript, str)
    assert isinstance(result.analysis, str)
    assert isinstance(result.tags, list)
    assert all(isinstance(tag, str) for tag in result.tags)
    assert isinstance(result.category, Category)
    assert isinstance(result.rating, int)
    assert 1 <= result.rating <= 10, "Rating should be between 1 and 10"
    assert isinstance(result.like, bool)

    # Save analysis to file
    analysis_dict = {
        "transcript": result.transcript,
        "analysis": result.analysis,
        "tags": result.tags,
        "category": result.category.value,
        "rating": result.rating,
        "like": result.like,
    }

    with open(output_fp, "w", encoding="utf-8") as f:
        json.dump(analysis_dict, f, indent=2)

    assert output_fp.exists(), "Analysis file was not created"
    assert output_fp.stat().st_size > 0, "Analysis file is empty"


@pytest.fixture(autouse=True)
async def cleanup(test_paths):
    """Cleanup any files created during the test"""
    yield
    # _, output_fp = test_paths
    # if output_fp.exists():
    #     output_fp.unlink()
