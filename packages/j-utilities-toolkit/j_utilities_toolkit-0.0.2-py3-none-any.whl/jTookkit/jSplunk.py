import pytz
import splunklib.client as client
import splunklib.results as results
from time import sleep


class SplunkClient:
    def __init__(self, host: str, port: int, username: str, password: str, scheme: str = "https"):
        """
        Initialize Splunk connection.
        """
        try:
            self.service = client.connect(
                host=host,
                port=port,
                username=username,
                password = password,
                scheme=scheme,
                verify=False
            )
        except Exception as ex:
            # Connection itself failed → bubble up as handled result
            self.service = None
            self.connection_error = str(ex)

    def query(self, query: str, earliest: str = "-24h", latest: str = "now") -> dict:
        """
        Run a Splunk query and return a structured result.

        :param query: SPL query string.
        :param earliest: Earliest time (default: -24h).
        :param latest: Latest time (default: now).
        :return: dict with {success, data, message}
        """
        if not self.service:
            return {
                "success": False,
                "data": [],
                "message": f"Failed to connect to Splunk: {self.connection_error}",
            }

        try:
            job = self.service.jobs.create(query, earliest_time=earliest, latest_time=latest)

            # Wait for job completion
            while not job.is_done():
                sleep(0.2)

            data = []
            for result in results.JSONResultsReader(job.results(output_mode="json")):
                if isinstance(result, dict):
                    data.append(result)

            if data:
                return {"success": True, "data": data}
            else:
                return {"success": False, "data": [], "message": "No data found"}

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"Error executing query '{query}': {e}",
            }