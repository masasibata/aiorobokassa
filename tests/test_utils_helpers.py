"""Tests for helper utilities."""

from aiorobokassa.utils.helpers import build_url, parse_shp_params


class TestBuildURL:
    """Tests for build_url function."""

    def test_build_url_with_params(self):
        """Test building URL with parameters."""
        base_url = "https://example.com/path"
        params = {"key1": "value1", "key2": "value2"}
        result = build_url(base_url, params)
        assert "key1=value1" in result
        assert "key2=value2" in result
        assert result.startswith(base_url)

    def test_build_url_without_params(self):
        """Test building URL without parameters."""
        base_url = "https://example.com/path"
        params = {}
        result = build_url(base_url, params)
        assert result == base_url

    def test_build_url_filters_none_values(self):
        """Test that None values are filtered out."""
        base_url = "https://example.com/path"
        params = {"key1": "value1", "key2": None, "key3": "value3"}
        result = build_url(base_url, params)
        assert "key1=value1" in result
        assert "key2" not in result
        assert "key3=value3" in result

    def test_build_url_with_existing_query(self):
        """Test building URL with existing query parameters."""
        base_url = "https://example.com/path?existing=value"
        params = {"new": "newvalue"}
        result = build_url(base_url, params)
        assert "existing=value" in result
        assert "new=newvalue" in result

    def test_build_url_encodes_special_characters(self):
        """Test that special characters are properly encoded."""
        base_url = "https://example.com/path"
        params = {"key": "value with spaces", "key2": "value&with=special"}
        result = build_url(base_url, params)
        assert "value+with+spaces" in result or "value%20with%20spaces" in result
        assert "value%26with%3Dspecial" in result or "value&with=special" in result


class TestParseShpParams:
    """Tests for parse_shp_params function."""

    def test_parse_shp_params_basic(self):
        """Test parsing basic Shp_ parameters."""
        params = {
            "OutSum": "100.50",
            "InvId": "12345",
            "Shp_param1": "value1",
            "Shp_param2": "value2",
        }
        result = parse_shp_params(params)
        assert result == {"param1": "value1", "param2": "value2"}

    def test_parse_shp_params_no_shp(self):
        """Test parsing when no Shp_ parameters exist."""
        params = {"OutSum": "100.50", "InvId": "12345"}
        result = parse_shp_params(params)
        assert result == {}

    def test_parse_shp_params_empty(self):
        """Test parsing empty parameters."""
        params = {}
        result = parse_shp_params(params)
        assert result == {}

    def test_parse_shp_params_mixed(self):
        """Test parsing mixed parameters."""
        params = {
            "OutSum": "100.50",
            "Shp_user_id": "123",
            "InvId": "456",
            "Shp_order_id": "789",
        }
        result = parse_shp_params(params)
        assert result == {"user_id": "123", "order_id": "789"}

    def test_parse_shp_params_case_sensitive(self):
        """Test that Shp_ prefix is case-sensitive."""
        params = {
            "Shp_param1": "value1",
            "shp_param2": "value2",  # lowercase, should be ignored
            "SHP_param3": "value3",  # uppercase, should be ignored
        }
        result = parse_shp_params(params)
        assert result == {"param1": "value1"}
