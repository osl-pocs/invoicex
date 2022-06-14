from asyncio import tasks
import sqlite3
from typing import Any
import pandas as pd
import datetime as dt

TTRACK_DB = "data_test/.timetrackdb"


class TTrack:
    def __init__(self, timetrackdb_file, parameters):
        self.timetrackdb = timetrackdb_file
        self.year_month = parameters.year_month
        self.tasks = parameters.ttrack_task

    def _conn_point(self):
        """Connect and point to .timetrackdb SQLite DB"""
        conn = sqlite3.connect(TTRACK_DB)
        cur = conn.cursor()
        return cur

    def _get_query(self, task=None):
        """Do the query defined by ttrack_tasks"""
        tasks_text = ", ".join([f'"{v}"' for v in tasks])
        return (
            "SELECT name, start, end FROM tasks AS T"
            " INNER JOIN tasklog AS L ON T.id=L.task"
            f" WHERE name IN ({tasks_text})"
            " ORDER BY start"
        )

    def _execute_query(self):
        """Execute the query and returns a list cointaining""" 
        """tasks with time in timestamp format"""
        cur = self._conn_point()
        entries_in_timestamp = []
        for row in cur.execute(
            self._get_query(self.tasks)  # TODO Except type error
        ):
            entries_in_timestamp.append(row)
        return entries_in_timestamp

    def _format_date(self):
        """Format timestamp date to datetime objects"""
        entries = self._execute_query()
        list_of_entries_with_formated_date = []
        for task, start, end in entries:
            start_f = dt.datetime.fromtimestamp(start)
            end_f = dt.datetime.fromtimestamp(end)
            list_of_entries_with_formated_date.append([task, start_f, end_f])
        return list_of_entries_with_formated_date

    def _prepare_dataframe(self):
        """Get the result and transform in a Pandas DataFrame"""
        raw_data = self._format_date()
        data = []
        for task, start, end in raw_data:
            time_worked = end - start
            task_dict = {
                "task": task,
                "date": start.strftime("%Y-%m-%d"),
                "time_worked": time_worked,
            }
            data.append(task_dict)
        df = pd.DataFrame(data=data).sort_values(["date"])
        return df

    def _filter_by_month(self, year_month=None):
        """Month is defined along with the Invoicex generation"""
        df = self._prepare_dataframe()
        if year_month is None:
            return df
        else:
            return df[df["date"].str.startswith(str(year_month))]

    def _group_tasks_remove_duplicates(self, v):
        tasks = v.to_string(index=False).split()
        unique_tasks = set(tasks)
        for t in unique_tasks:
            return ", ".join(str(t) for t in unique_tasks)

    def _group_time_and_sum(self, v):
        return v.sum()

    def _generate_dataframe(self):
        """Create the final DataFrame"""
        df = self._filter_by_month(self.year_month)
        df_grouped = df.groupby("date").aggregate(
            lambda v: self._group_tasks_remove_duplicates(v)
            if v.name == "task"
            else self._group_time_and_sum(v)
        )
        return df_grouped


def get_data(args) -> pd.DataFrame:
    """ """
    database = TTRACK_DB
    ttrack_df = TTrack(database, args)
    return ttrack_df._generate_dataframe()
