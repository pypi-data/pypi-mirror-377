import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from playwright_analyzer.report_parser import PlaywrightReportParser


class TestPlaywrightReportParser:
    @pytest.fixture
    def parser(self):
        return PlaywrightReportParser()

    def test_parser_initialization(self, parser):
        assert parser is not None
        assert hasattr(parser, 'parse_report')

    @pytest.mark.asyncio
    async def test_parse_empty_report(self, parser):
        with pytest.raises(ValueError):
            await parser.parse_report("")

    @pytest.mark.asyncio
    async def test_parse_invalid_html(self, parser):
        invalid_html = "<html><body>Invalid report</body></html>"
        with pytest.raises(ValueError):
            await parser.parse_report(invalid_html)