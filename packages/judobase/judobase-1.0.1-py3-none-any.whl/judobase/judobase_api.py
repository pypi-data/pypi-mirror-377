# flake8: noqa: WPS215

import asyncio
from datetime import datetime

from judobase.base import CompetitionAPI, ContestAPI, CountryAPI, CountryShort, JudokaAPI
from judobase.schemas import WEIGHT_ID_MAPPING, Competition, Contest, Country, Judoka, WeightEnum


class JudoBase(CompetitionAPI, ContestAPI, JudokaAPI, CountryAPI):
    """Class for extended interacting with the JudoBase API.

    Provides methods to retrieve information about competitions, contests, judokas, and countries.
    """

    async def all_competition(self) -> list[Competition]:
        """Retrieves data for all competitions."""
        return await self.get_competition_list()

    async def competitions_in_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Competition]:
        """Retrieves data for competitions within a specified date range."""
        all_comps = await self.all_competition()
        return [comp for comp in all_comps if start_date <= comp.date_from <= end_date]

    async def competition_by_id(self, competition_id: int | str) -> Competition:
        """Retrieves data for a specific competition by its ID."""
        return await self.get_competition_info(str(competition_id))

    async def all_contests(self) -> list[Contest]:
        """Retrieves data for all contests using concurrent API calls."""
        comps = await self.all_competition()
        tasks = [self.find_contests(comp.id_competition) for comp in comps]
        tasks_results = await asyncio.gather(*tasks)

        return [contest for sublist in tasks_results for contest in sublist]


    async def contests_by_competition_id(
        self,
        competition_id: int | str,
        weight: WeightEnum = "",
        *,
        include_events: bool = False
    ) -> list[Contest]:
        """Retrieves data for all contests using concurrent API calls.

        Optionally filters by weight category and includes data about contests events like
        throw, osaekomi or shido.
        """
        contests = await self.find_contests(
            competition_id=str(competition_id),
            weight_id=WEIGHT_ID_MAPPING[weight] if weight else ""
        )
        if include_events:
            tasks = [
                self.find_contests(
                    contest_code=contest.contest_code_long,
                    include="info,events"
                )
                for contest in contests
            ]
            tasks_results = await asyncio.gather(*tasks)
            contests = [contest for sublist in tasks_results for contest in sublist]

        return contests

    async def judoka_by_id(self, judoka_id: int | str) -> Judoka:
        """Retrieves data for a specific judoka by their ID."""
        return await self.get_judoka_info(str(judoka_id))

    async def country_by_id(self, country_id: int | str) -> Country:
        """Retrieves data for a specific country by its ID."""
        return await self.get_country_info(str(country_id))

    async def all_countries(self) -> list[CountryShort]:
        """Retrieves short data for all the countries."""
        return await self.get_country_list()
