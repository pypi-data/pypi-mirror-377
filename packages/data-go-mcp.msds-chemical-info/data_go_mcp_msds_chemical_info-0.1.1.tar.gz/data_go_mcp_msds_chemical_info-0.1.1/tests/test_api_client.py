"""Tests for MSDS Chemical Info API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import xml.etree.ElementTree as ET
from data_go_mcp.msds_chemical_info.api_client import MsdsChemicalInfoAPIClient
from data_go_mcp.msds_chemical_info.models import SearchType, ChemicalListItem


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key fixture."""
    monkeypatch.setenv("API_KEY", "test-api-key")
    return "test-api-key"


@pytest.fixture
def client(mock_api_key):
    """Create API client fixture."""
    return MsdsChemicalInfoAPIClient(api_key=mock_api_key)


def create_xml_response(result_code="00", result_msg="NORMAL SERVICE.", body_content=""):
    """Helper to create XML response."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>{result_code}</resultCode>
        <resultMsg>{result_msg}</resultMsg>
    </header>
    <body>
        {body_content}
    </body>
</response>"""


def create_list_body(items, total_count=1, page_no=1, num_of_rows=10):
    """Helper to create list response body."""
    items_xml = ""
    for item in items:
        items_xml += f"""
        <item>
            <casNo>{item.get('casNo', '')}</casNo>
            <chemId>{item.get('chemId', '')}</chemId>
            <chemNameKor>{item.get('chemNameKor', '')}</chemNameKor>
            <enNo>{item.get('enNo', '')}</enNo>
            <keNo>{item.get('keNo', '')}</keNo>
            <unNo>{item.get('unNo', '')}</unNo>
            <lastDate>{item.get('lastDate', '')}</lastDate>
            <koshaConfirm>{item.get('koshaConfirm', '')}</koshaConfirm>
            <openYn>{item.get('openYn', '')}</openYn>
        </item>"""

    return f"""
        <items>{items_xml}
        </items>
        <totalCount>{total_count}</totalCount>
        <pageNo>{page_no}</pageNo>
        <numOfRows>{num_of_rows}</numOfRows>
    """


def create_detail_body(items):
    """Helper to create detail response body."""
    items_xml = ""
    for item in items:
        items_xml += f"""
        <item>
            <lev>{item.get('lev', 1)}</lev>
            <msdsItemCode>{item.get('msdsItemCode', '')}</msdsItemCode>
            <upMsdsItemCode>{item.get('upMsdsItemCode', '')}</upMsdsItemCode>
            <msdsItemNameKor>{item.get('msdsItemNameKor', '')}</msdsItemNameKor>
            <msdsItemNo>{item.get('msdsItemNo', '')}</msdsItemNo>
            <ordrIdx>{item.get('ordrIdx', 0)}</ordrIdx>
            <itemDetail>{item.get('itemDetail', '')}</itemDetail>
        </item>"""

    return f"""<items>{items_xml}</items>"""


@pytest.mark.asyncio
async def test_search_chemicals_success(client):
    """Test successful chemical search."""
    body_content = create_list_body([
        {
            'casNo': '71-43-2',
            'chemId': '000100',
            'chemNameKor': '벤젠',
            'keNo': 'KE-02380',
            'lastDate': '2023-01-01'
        }
    ])

    xml_response = create_xml_response(body_content=body_content)

    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = xml_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await client.search_chemicals("벤젠", SearchType.KOREAN_NAME, 1, 10)

        assert len(result.items) == 1
        assert result.items[0].chem_name_kor == '벤젠'
        assert result.items[0].cas_no == '71-43-2'
        assert result.items[0].chem_id == '000100'


@pytest.mark.asyncio
async def test_search_chemicals_empty_result(client):
    """Test chemical search with no results."""
    body_content = create_list_body([], total_count=0)
    xml_response = create_xml_response(body_content=body_content)

    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = xml_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await client.search_chemicals("없는화학물질", SearchType.KOREAN_NAME)

        assert len(result.items) == 0
        assert result.total_count == 0


@pytest.mark.asyncio
async def test_get_chemical_detail(client):
    """Test getting chemical detail section."""
    body_content = create_detail_body([
        {
            'lev': 1,
            'msdsItemCode': 'A02',
            'msdsItemNameKor': '제품명',
            'msdsItemNo': '가',
            'itemDetail': '벤젠',
            'ordrIdx': 1002
        },
        {
            'lev': 1,
            'msdsItemCode': 'A04',
            'msdsItemNameKor': '제품의 권고 용도와 사용상의 제한',
            'msdsItemNo': '나',
            'itemDetail': '자료없음',
            'ordrIdx': 1004
        }
    ])

    xml_response = create_xml_response(body_content=body_content)

    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = xml_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await client.get_chemical_detail("000100", 1)

        assert result.section_number == 1
        assert result.section_title == "화학제품과 회사에 관한 정보"
        assert len(result.items) == 2
        assert result.items[0].msds_item_name_kor == '제품명'
        assert result.items[0].item_detail == '벤젠'


@pytest.mark.asyncio
async def test_detect_search_type_cas():
    """Test CAS number detection."""
    client = MsdsChemicalInfoAPIClient(api_key="test")

    assert client.detect_search_type("71-43-2") == SearchType.CAS_NO
    assert client.detect_search_type("50-00-0") == SearchType.CAS_NO


@pytest.mark.asyncio
async def test_detect_search_type_un():
    """Test UN number detection."""
    client = MsdsChemicalInfoAPIClient(api_key="test")

    assert client.detect_search_type("UN1234") == SearchType.UN_NO
    assert client.detect_search_type("1234") == SearchType.UN_NO


@pytest.mark.asyncio
async def test_detect_search_type_ke():
    """Test KE number detection."""
    client = MsdsChemicalInfoAPIClient(api_key="test")

    assert client.detect_search_type("KE-12345") == SearchType.KE_NO
    assert client.detect_search_type("ke-12345") == SearchType.KE_NO


@pytest.mark.asyncio
async def test_detect_search_type_en():
    """Test EN number detection."""
    client = MsdsChemicalInfoAPIClient(api_key="test")

    assert client.detect_search_type("200-001-8") == SearchType.EN_NO
    assert client.detect_search_type("231-195-2") == SearchType.EN_NO


@pytest.mark.asyncio
async def test_detect_search_type_korean():
    """Test Korean name detection (default)."""
    client = MsdsChemicalInfoAPIClient(api_key="test")

    assert client.detect_search_type("벤젠") == SearchType.KOREAN_NAME
    assert client.detect_search_type("메탄올") == SearchType.KOREAN_NAME
    assert client.detect_search_type("황산") == SearchType.KOREAN_NAME


@pytest.mark.asyncio
async def test_api_error_response(client):
    """Test handling of API error response."""
    xml_response = create_xml_response(
        result_code="99",
        result_msg="SERVICE ERROR"
    )

    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = xml_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="API error: SERVICE ERROR"):
            await client.search_chemicals("test", SearchType.KOREAN_NAME)


@pytest.mark.asyncio
async def test_invalid_xml_response(client):
    """Test handling of invalid XML response."""
    with patch.object(client.client, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = "Invalid XML <<<"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to parse XML response"):
            await client.search_chemicals("test", SearchType.KOREAN_NAME)


@pytest.mark.asyncio
async def test_get_all_chemical_details(client):
    """Test getting all chemical details."""
    # Create mock responses for all 16 sections
    mock_responses = []
    for i in range(1, 17):
        body_content = create_detail_body([
            {
                'lev': 1,
                'msdsItemCode': f'S{i:02d}',
                'msdsItemNameKor': f'섹션 {i} 정보',
                'itemDetail': f'섹션 {i} 내용',
                'ordrIdx': i * 100
            }
        ])
        mock_responses.append(create_xml_response(body_content=body_content))

    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        mock_response = MagicMock()
        mock_response.text = mock_responses[call_count]
        mock_response.raise_for_status = MagicMock()
        call_count += 1
        return mock_response

    with patch.object(client.client, 'get', side_effect=mock_get):
        results = await client.get_all_chemical_details("000100")

        assert len(results) == 16
        for i in range(1, 17):
            assert i in results
            assert results[i].section_number == i


def test_client_initialization_without_api_key():
    """Test client initialization without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="API key is required"):
            MsdsChemicalInfoAPIClient()


def test_client_initialization_with_env_api_key(monkeypatch):
    """Test client initialization with environment API key."""
    monkeypatch.setenv("API_KEY", "env-api-key")
    client = MsdsChemicalInfoAPIClient()
    assert client.api_key == "env-api-key"


def test_client_initialization_with_param_api_key():
    """Test client initialization with parameter API key."""
    client = MsdsChemicalInfoAPIClient(api_key="param-api-key")
    assert client.api_key == "param-api-key"