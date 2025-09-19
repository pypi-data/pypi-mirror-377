import pytest
from unittest.mock import Mock, patch, AsyncMock
from playwright_analyzer.agent import PlaywrightAnalyzer


class TestPlaywrightAnalyzer:
    @pytest.fixture
    def analyzer(self):
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            return PlaywrightAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')

    @pytest.mark.asyncio
    async def test_analyze_empty_input(self, analyzer):
        with pytest.raises(ValueError):
            await analyzer.analyze("")

    @pytest.mark.asyncio
    async def test_analyze_with_mock_response(self, analyzer):
        with patch.object(analyzer, 'agent') as mock_agent:
            mock_agent.run.return_value = AsyncMock(data="Test analysis result")
            result = await analyzer.analyze("test input")
            assert result is not None