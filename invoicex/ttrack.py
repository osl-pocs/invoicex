"""
import sqlite3
from humanfriendly import format_timespan

TTRACK_DB = 'data_test/.timetrackdb'

def _get_list_of_tasks_entries_with_time_in_seconds(sql_database):
    conn = sqlite3.connect(sql_database)
    cur = conn.cursor()
    entries_with_seconds = []
    for row in cur.execute(f"SELECT name, (end - start) FROM tasks AS T"
                            " INNER JOIN tasklog AS L ON T.id=L.task"
                            " ORDER BY name"):
        entries_with_seconds.append(row)
    return entries_with_seconds


def _isolate_same_tasks_in_list():
    entries = _get_list_of_tasks_entries_with_time_in_seconds(TTRACK_DB)
    same = {t:0 for t, s in entries}
    for task, secs in entries:
        same[task] += secs
    result = list(map(tuple, same.items()))
    return result

def _return_index_of_tasks_in_hours():
    tasks = _isolate_same_tasks_in_list()
    for t, s in tasks:
        print(f'{t} ---- {format_timespan(s)}')


_return_index_of_tasks_in_hours()

"""
