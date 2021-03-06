# # -*- coding: utf-8 -*-
import requests

from tools import parse_string_date

Q = "&q={0}"
base_url = "https://data.gov.il"
url_s = 'https://data.gov.il/api/action/datastore_search?resource_id=7c8255d0-49ef-49db-8904-4cf917586031'


class MehirLameshtakenApi(object):
    def __init__(self):
        self._results = []
        self.cache_results = []
        self._filters = []
        self._total = 0
        self._url = ""

    def add_filter(self, filter_dict):
        """Adds a filter"""
        self._filters.append(filter_dict)

    def fetch_query(self):
        """Fetches api query after filters was set"""
        self._get_all_data()

    def get_results(self):
        """Fetches results"""
        return self._results

    def _get_all_data(self):
        self._url = url_s
        self._extract_all_data()

    def _extract_all_data(self):
        if not self.cache_results:
            results = self._make_call(self._url)
            self._append_records(results)
            total = self._get_total_results(results)
            self._total = total - len(self._results)

            while self._total != 0:
                path = self._get_next_path(results)
                new_url = self._create_next_url(path)
                results = self._make_call(new_url)
                records = self._append_records(results)
                self._total = self._total - len(records)
        else:
            self._results = self.cache_results.copy()

        print("finished fetch_query")

        self._filter_results()

    @staticmethod
    def _get_total_results(results):
        return results["result"]["total"]

    def _get_next_path(self, results):
        return results["result"]["_links"]["next"]

    @staticmethod
    def _make_call(uri):
        fileobj = requests.get(uri)
        return fileobj.json()

    @staticmethod
    def _parse_filter_string(filter_string):
        return {"filter_field": filter_string.split(":")[0], "filter_value": filter_string.split(":")[1]}

    def _append_records(self, results):
        new_results = results["result"]["records"]
        parsed_new_results = parse_string_date(new_results, "תאריך סיום רישום", "תאריך ביצוע הגרלה")
        self._results.extend(parsed_new_results)
        self.cache_results = self._results.copy()
        return parsed_new_results

    @staticmethod
    def _create_next_url(path):
        return "{}{}".format(base_url, path)

    def _filter_results(self):
        for filter_row in self._filters:
            filter_field = filter_row["filter_field"]
            filter_value = filter_row["filter_value"]
            self._results = \
                list(filter(lambda x: x[filter_field] == filter_value, self._results))



if __name__ == "__main__":
    query_api = MehirLameshtakenApi()
    query_api.fetch_query()
    a = query_api.get_results()
    for i in a:
        print(i)