import dataclasses
import re
from typing import List, Optional

import pandas as pd
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from jinja2 import Template


class GitHubGraphQL:
    token: str = ""
    transport: Client = None

    def __init__(self, parameters):
        self.token = parameters.token
        self.user = parameters.gh_user
        self.repos = parameters.gh_repos
        self.year_month = parameters.year_month

        self.transport = AIOHTTPTransport(
            headers={"Authorization": f"bearer {self.token}"},
            url="https://api.github.com/graphql",
        )

        self.gql_template = '''
        query ($first: Int!) {
            search(
                query: """{query}""",
                type: ISSUE,
                first: $first
            ) {
                nodes {
                    ... on Issue {
                        author {
                           login
                        }
                        number
                        comments(first: $first) {
                            nodes {
                                updatedAt
                                createdAt
                                author {
                                   login
                                }
                            }
                        }
                        createdAt
                        updatedAt
                        title
                    }
                    ... on PullRequest {
                        author {
                           login
                        }
                        number
                        comments(first: $first) {
                            nodes {
                                updatedAt
                                createdAt
                                author {
                                   login
                                }
                            }
                        }
                        createdAt
                        updatedAt
                        mergedAt
                        title
                        commits(first: $first) {
                            nodes {
                                commit {
                                    id
                                    author {
                                        user {
                                            login
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        '''

    async def _pagination(self, gql_tmpl, variables):
        has_next_page = True
        pagination_after = ""
        limit = 100
        results = []

        while has_next_page:
            _variables = dict(variables)
            _variables.update(
                after=""
                if not pagination_after
                else f', after: "{pagination_after}"'
            )
            tmpl = Template(gql_tmpl)
            gql_stmt = tmpl.render(**_variables)
            # print(gql_stmt)

            query = gql(gql_stmt)
            params = {"first": limit}

            result = await self.session.execute(query, variable_values=params)

            try:
                has_next_page = result["search"]["pageInfo"]["hasNextPage"]
                pagination_after = result["search"]["pageInfo"]["endCursor"]
            except (IndexError, KeyError):
                has_next_page = False

            if result.get("search", {}).get("nodes"):
                results += result["search"]["nodes"]

        return results

    async def _search_issues(self):
        query = " ".join([f"repo:{repo}" for repo in self.repos])
        query += " is:issue"
        gql = self.gql_template.replace("{query}", query)
        return await self._prepare_issues(await self._pagination(gql, {}))

    async def _search_pull_requests(self):
        query = " ".join([f"repo:{repo}" for repo in self.repos])
        query += " is:pr"
        gql = self.gql_template.replace("{query}", query)
        return await self._prepare_prs(await self._pagination(gql, {}))

    async def _prepare_issues(self, raw_data: list) -> pd.DataFrame:
        data = []

        for row in raw_data:
            if row["author"]["login"] == self.user:
                created_at = row["createdAt"][:10]
                if created_at[:7] == self.year_month:
                    data.append(
                        {
                            "datetime": created_at,
                            "time": "00:00",  # user need to do it manually
                            "action": f"Issues reported",
                        }
                    )
            for comment in row["comments"]["nodes"]:
                if comment["author"]["login"] != self.user:
                    continue
                created_at = comment["createdAt"][:10]
                if self.year_month == created_at[:7]:
                    data.append(
                        {
                            "datetime": created_at,
                            "time": "00:00",  # user need to do it manually
                            "action": f"Issues discussed",
                        }
                    )
        result = pd.DataFrame(data)
        if result.empty:
            result = pd.DataFrame(
                {"datetime": [], "time": "00:00", "action": []}
            )
        return (
            result.sort_values("datetime")
            .drop_duplicates()
            .reset_index(drop=True)
        )

    async def _prepare_prs(self, raw_data: list) -> pd.DataFrame:
        data = []

        for row in raw_data:
            created_at = row["createdAt"][:10]
            merged_at = row.get("mergeddAt")

            if row["author"]["login"] == self.user:
                if created_at[:7] == self.year_month:
                    data.append(
                        {
                            "datetime": created_at,
                            "time": "00:00",  # user need to do it manually
                            "action": f"PR#{row['number']}: {row['title']}",
                        }
                    )
            # breakpoint()
            for comment in row["comments"]["nodes"]:
                if comment["author"]["login"] != self.user:
                    continue

                created_at = comment["createdAt"][:10]
                if self.year_month == created_at[:7]:
                    data.append(
                        {
                            "datetime": created_at,
                            "time": "00:00",  # user need to do it manually
                            "action": f"PR#{row['number']}: {row['title']}",
                        }
                    )

            for commit in row["commits"]["nodes"]:
                if commit.get("author", {}).get("user", {}).get("login") != self.user:
                    continue

                created_at = comment["createdAt"][:10]
                if self.year_month == created_at[:7]:
                    data.append(
                        {
                            "datetime": created_at,
                            "time": "00:00",  # user need to do it manually
                            "action": f"PR#{row['number']}: {row['title']}",
                        }
                    )
        result = pd.DataFrame(data)
        if result.empty:
            result = pd.DataFrame(
                {"datetime": [], "time": "00:00", "action": []}
            )
        return (
            result.sort_values("datetime")
            .drop_duplicates()
            .reset_index(drop=True)
        )

    async def _summarize(self, data: pd.DataFrame):
        return (
            data.groupby("datetime")
            .agg(lambda row: "\n".join([f"- {v}" for v in set(row)]))
            .reset_index()
        )

    async def get_data(self):
        async with Client(
            transport=self.transport,
            fetch_schema_from_transport=True,
        ) as session:
            self.session = session
            result = [
                await self._search_issues(),
                await self._search_pull_requests(),
            ]
        return await self._summarize(pd.concat(result))


async def get_data(args) -> pd.DataFrame:
    """ """
    ghgql = GitHubGraphQL(args)
    return await ghgql.get_data()
