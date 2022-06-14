import sqlite3
from typing import Any
import pandas as pd
import datetime as dt
import os

TTRACK_DB = "data_test/.timetrackdb"


class TTrack:
    def __init__(self, timetrackdb_file) -> os.path:
        self.timetrackdb = timetrackdb_file

    def _conn_point(self):
        conn = sqlite3.connect(self.timetrackdb)
        cur = conn.cursor()
        return cur

    def _get_query(self, task=None):
        if task is None:
            return (
                "SELECT name, start, end FROM tasks AS T"
                " INNER JOIN tasklog AS L ON T.id=L.task"
                " ORDER BY start"
            )
        if ", " in task:
            tasks = task.split(", ")
            other = []
            for x in tasks[1:]:
                other.append(f" OR name='{x}'")
            return (
                "SELECT name, start, end FROM tasks AS T"
                " INNER JOIN tasklog AS L ON T.id=L.task"
                f" WHERE name='{tasks[0]}'"
                f" {''.join(other)}"
                " ORDER BY start"
            )
        else:
            return (
                "SELECT name, start, end FROM tasks AS T"
                " INNER JOIN tasklog AS L ON T.id=L.task"
                f" WHERE name='{task}'"
                " ORDER BY start"
            )

    def _get_list_of_tasks_entries_in_timestamp(self):
        cur = self._conn_point()
        entries_in_timestamp = []
        for row in cur.execute(
            self._get_query()
        ):  # TODO Externalize _get_query() to receive params from func call
            entries_in_timestamp.append(row)
        return entries_in_timestamp

    def _format_unix_time_to_datetime_obj_in_lists(self):
        entries = self._get_list_of_tasks_entries_in_timestamp()
        list_of_entries_with_formated_date = []
        for task, start, end in entries:
            start_f = dt.datetime.fromtimestamp(start)
            end_f = dt.datetime.fromtimestamp(end)
            list_of_entries_with_formated_date.append([task, start_f, end_f])
        return list_of_entries_with_formated_date

    def _prepare_dataframe(self):
        raw_data = self._format_unix_time_to_datetime_obj_in_lists()
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
        df = self._prepare_dataframe()
        if year_month is None:
            return df
        else:
            return df[df["date"].str.contains(str(year_month))]

    def _group_tasks_remove_duplicates(self, v):
        tasks = v.to_string(index=False).split()
        unique_tasks = set(tasks)
        for t in unique_tasks:
            return ", ".join(str(t) for t in unique_tasks)

    def _group_time_and_sum(self, v):
        return v.sum()

    def _group_tasks_and_time(self):
        df = self._filter_by_month(
            "2022-06"
        )  # TODO Externalize _filter_by_month to the same function that _get_query()
        print(df)
        df_grouped = df.groupby("date").aggregate(
            lambda v: self._group_tasks_remove_duplicates(v)
            if v.name == "task"
            else self._group_time_and_sum(v)
        )
        return df_grouped

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self._group_tasks_and_time()


# e = TTrack(TTRACK_DB)
# print(e())
