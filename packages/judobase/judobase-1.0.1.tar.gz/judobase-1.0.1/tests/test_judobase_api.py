from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from judobase import Competition, Contest, JudoBase


class TestJudobase:
    """Test cases for the Judobase class."""

    @patch("judobase.base.CompetitionAPI.get_competition_list")
    @pytest.mark.asyncio
    async def test_all_competition(self, mock_get_competition_list):
        """Test all_competition response."""
        async with JudoBase() as client:
            await client.all_competition()
            mock_get_competition_list.assert_called_once_with()

    @patch("judobase.base.CompetitionAPI.get_competition_list", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_competitions_in_range(self, mock_get_competition_list, get_test_data):
        """Test competitions_in_range response."""
        test_data = get_test_data("competitions_in_range.json")
        mock_get_competition_list.return_value = [
            Competition(**comp) for comp in test_data["mock_response"]
        ]

        async with JudoBase() as client:
            comps = await client.competitions_in_range(
                datetime(2023,5,1, tzinfo=timezone.utc),
                datetime(2023, 8, 1, tzinfo=timezone.utc),
            )
            mock_get_competition_list.assert_called_once_with()
            assert comps == [Competition(**comp) for comp in test_data["expected"]]

    @patch("judobase.base.ContestAPI.find_contests", new_callable=AsyncMock)
    @patch("judobase.base.CompetitionAPI.get_competition_list", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_all_contests(self, mock_get_competition_list, mock_find_contests, get_test_data):
        """Test all_contests response."""
        test_data = get_test_data("competitions_in_range.json")
        mock_get_competition_list.return_value = [
            Competition(**comp) for comp in test_data["mock_response"]
        ]
        async with JudoBase() as client:
            await client.all_contests()
            mock_get_competition_list.assert_called_once_with()
            assert mock_find_contests.call_count == len(test_data["mock_response"])

    @patch("judobase.base.ContestAPI.find_contests", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_contests_by_competition_id(
        self,
        mock_find_contests,
        get_test_data
    ):
        """Test contests_by_competition_id response."""
        test_data = get_test_data("contests_by_competition_id.json")
        mock_find_contests.return_value = [
            Contest(**cont) for cont in test_data["mock_response"]
        ]
        async with JudoBase() as client:
            await client.contests_by_competition_id(competition_id=2869)
            mock_find_contests.called_once_with("2869")

            mock_find_contests.reset_mock()
            await client.contests_by_competition_id(
                competition_id=2869,
                include_events=True
            )
            assert mock_find_contests.call_count == len(test_data["mock_response"]) + 1

    @patch("judobase.base.CompetitionAPI.get_competition_info")
    @pytest.mark.asyncio
    async def test_competition_by_id(self, mock_competition_by_id):
        """Test competition_by_id response."""
        async with JudoBase() as client:
            await client.competition_by_id(123)
            mock_competition_by_id.assert_called_once_with("123")

    @patch("judobase.base.JudokaAPI.get_judoka_info")
    @pytest.mark.asyncio
    async def test_judoka_by_id(self, mock_get_judoka_info):
        """Test judoka_by_id response."""
        async with JudoBase() as client:
            await client.judoka_by_id(123)
            mock_get_judoka_info.assert_called_once_with("123")

    @patch("judobase.base.CountryAPI.get_country_info")
    @pytest.mark.asyncio
    async def test_country_by_id(self, mock_get_country_info):
        """Test country_by_id response."""
        async with JudoBase() as client:
            await client.country_by_id(123)
            mock_get_country_info.assert_called_once_with("123")

    @patch("judobase.base.CountryAPI.get_country_list")
    @pytest.mark.asyncio
    async def test_all_countries(self, mock_get_country_list):
        """Test all_countries response."""
        async with JudoBase() as client:
            await client.all_countries()
            mock_get_country_list.assert_called_once_with()
