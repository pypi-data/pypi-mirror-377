"""Tests for MSDS Chemical Info MCP server."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from data_go_mcp.msds_chemical_info.server import (
    search_chemicals,
    get_chemical_safety_summary,
    get_chemical_handling_info,
    get_chemical_properties,
    get_chemical_regulatory_info,
    get_chemical_section,
    get_complete_msds
)
from data_go_mcp.msds_chemical_info.models import (
    ChemicalListItem, ChemicalListResponse, MsdsSection, MsdsDetailItem
)


@pytest.fixture
def mock_client():
    """Mock API client fixture."""
    with patch('data_go_mcp.msds_chemical_info.server.MsdsChemicalInfoAPIClient') as mock:
        client_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = client_instance
        yield client_instance


@pytest.mark.asyncio
async def test_search_chemicals_success(mock_client):
    """Test successful chemical search."""
    from data_go_mcp.msds_chemical_info.models import SearchType

    mock_response = ChemicalListResponse(
        items=[
            ChemicalListItem(
                chemId="000100",
                chemNameKor="벤젠",
                casNo="71-43-2",
                keNo="KE-02380",
                unNo="1114",
                enNo="200-753-7",
                lastDate="2023-01-01"
            )
        ],
        totalCount=1,
        pageNo=1,
        numOfRows=10
    )
    mock_client.search_chemicals.return_value = mock_response
    mock_client.detect_search_type.return_value = SearchType.KOREAN_NAME

    result = await search_chemicals("벤젠")

    assert len(result["items"]) == 1
    assert result["items"][0]["chem_name_kor"] == "벤젠"
    assert result["items"][0]["chem_id"] == "000100"
    assert result["total_count"] == 1


@pytest.mark.asyncio
async def test_get_chemical_safety_summary_success(mock_client):
    """Test getting chemical safety summary."""
    mock_sections = {
        "section_1": MsdsSection(
            section_number=1,
            section_title="화학제품과 회사에 관한 정보",
            items=[
                MsdsDetailItem(
                    lev=1,
                    msdsItemCode="A02",
                    msdsItemNameKor="제품명",
                    msdsItemNo="가",
                    itemDetail="벤젠",
                    ordrIdx=1002
                )
            ]
        ),
        "section_2": MsdsSection(
            section_number=2,
            section_title="유해성·위험성",
            items=[]
        ),
        "section_3": MsdsSection(
            section_number=3,
            section_title="구성성분의 명칭 및 함유량",
            items=[]
        ),
        "section_4": MsdsSection(
            section_number=4,
            section_title="응급조치요령",
            items=[]
        )
    }
    mock_client.get_safety_summary.return_value = mock_sections

    result = await get_chemical_safety_summary("000100")

    assert "section_1" in result
    assert result["section_1"]["title"] == "화학제품과 회사에 관한 정보"
    assert "제품명" in result["section_1"]["content"]
    assert "벤젠" in result["section_1"]["content"]


@pytest.mark.asyncio
async def test_get_chemical_section_invalid_number(mock_client):
    """Test getting chemical section with invalid number."""
    result = await get_chemical_section("000100", 17)  # Invalid section number

    assert "error" in result
    assert "Invalid section number" in result["error"]
    assert "available_sections" in result


@pytest.mark.asyncio
async def test_get_complete_msds_success(mock_client):
    """Test getting complete MSDS information."""
    mock_sections = {
        i: MsdsSection(
            section_number=i,
            section_title=f"섹션 {i}",
            items=[
                MsdsDetailItem(
                    lev=1,
                    msdsItemCode=f"S{i:02d}",
                    msdsItemNameKor=f"항목 {i}",
                    itemDetail=f"내용 {i}",
                    ordrIdx=i * 100
                )
            ]
        ) for i in range(1, 17)
    }
    mock_client.get_all_chemical_details.return_value = mock_sections

    result = await get_complete_msds("000100")

    assert "sections" in result
    assert len(result["sections"]) == 16
    for i in range(1, 17):
        section_key = f"section_{i}"
        assert section_key in result["sections"]
        assert result["sections"][section_key]["number"] == i