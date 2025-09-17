import urllib3

# Disable SSL warnings since we intentionally use verify=False for internal services
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from graphql import parse, print_ast
from .configuration import Configuration_Mutation
from .configuration import Configuration_Query
from .device_info import Device_Info_Mutation
from .device_info import Device_Info_Query
from .device_connection import Device_Connections_Mutation
from .device_connection import Device_Connections_Query

from .device_version import Device_Version_Query
from .device_version import Device_Version_Mutation
from .device_status import Device_Status_Mutation
from .device_status import Device_Status_Query
from .dtc import Dtc_Query
from .dtc import Dtc_Mutation
from .ecu import Ecu_Query
from .formula import Formula_Mutation
from .formula import Formula_Query
from .gps import GPS_Mutation
from .gps import GPS_Query
from .message import Message_Mutation
from .message import Message_Query
from .network_stats import Network_Stats_Mutation
from .network_stats import Network_Stats_Query
from .network import Network_Query
from .signal import Signals_Query
from .signal import Signals_Mutation
from .version import Version_Mutation
from .version import Version_Query
from .fail_processing import FailProcessingMutation
from .fail_processing import FailProcessingQuery

from requests.exceptions import RequestException
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GraphQL_Client:
    def __init__(self, endpoint, max_retries, retry_delay):
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    import requests

    def execute(self, query, variables=None):
        # Ensure at least one attempt is made even if self.max_retries is 0
        retries = self.max_retries + 1

        for attempt in range(1, retries + 1):
            try:
                request_data = {
                    "query": print_ast(parse(query)),
                    "variables": variables,
                }
                response = requests.post(self.endpoint, json=request_data, verify=False)

                if not response.text:
                    print("Empty response received.")
                    return {"data": None, "errors": "Empty response"}

                try:
                    response_data = response.json()
                except ValueError as e:
                    print("Failed to decode JSON:", e)
                    return {"data": None, "errors": "Invalid JSON response"}

                if "errors" in response_data:
                    print("GraphQL request had errors:", response_data["errors"])
                    return {"data": None, "errors": response_data["errors"]}

                return {"data": response_data["data"]}

            except RequestException as e:
                if attempt == retries:
                    print(
                        f"Failed to connect after {retries-1} attempts. Last error: {str(e)}"
                    )
                    raise RuntimeError(
                        f"Connection failed after {retries-1} retries: {e}"
                    )

                print(
                    f"Connection attempt {attempt} failed. Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)

    # Configuration Functions:
    def create_configuration(self, variables=None):
        mutation = Configuration_Mutation.create_configuration_mutation
        return self.execute(mutation, variables)

    def get_configuration(self, variables=None):
        query = Configuration_Query.get_configuration_query
        return self.execute(query, variables)

    # Device info Functions:
    # def create_device_status(self, variables=None):
    #     mutation = Device_Info_Mutation.create_device_info_mutation
    #     return self.execute(mutation, variables)

    # def delete_device_info(self, variables=None):
    #     mutation = Device_Info_Mutation.delete_device_info_mutation
    #     return self.execute(mutation, variables)

    # def get_device_info(self, variables=None):
    #     query = Device_Info_Query.get_device_info_query
    #     return self.execute(query, variables)
    # Device Connection Functions
    def create_device_connection(self, variables=None):
        mutation = Device_Connections_Mutation.upsert_device_connection_mutation
        return self.execute(mutation, variables)

    def delete_device_connection(self, variables=None):
        mutation = Device_Connections_Mutation.delete_device_connection_mutation
        return self.execute(mutation, variables)

    def get_device_connection(self, variables=None):
        query = Device_Connections_Query.get_device_connection_query
        return self.execute(query, variables)

    # Device status Functions:
    def create_device_status(self, variables=None):
        mutation = Device_Status_Mutation.create_device_status_mutation
        return self.execute(mutation, variables)

    def delete_device_status(self, variables=None):
        mutation = Device_Status_Mutation.delete_device_status_mutation
        return self.execute(mutation, variables)

    def get_device_status(self, variables=None):
        query = Device_Status_Query.get_device_status_query
        return self.execute(query, variables)

    # Device version Functions:
    def create_device_version(self, variables=None):
        mutation = Device_Version_Mutation.upsert_device_version_mutation
        return self.execute(mutation, variables)

    def delete_device_version(self, variables=None):
        mutation = Device_Version_Mutation.delete_device_version_mutation
        return self.execute(mutation, variables)

    def get_device_version(self, variables=None):
        query = Device_Version_Query.get_device_version_query
        return self.execute(query, variables)

    # DTC Functions:
    def create_dtc(self, variables=None):
        mutation = Dtc_Mutation.upsert_dtc_mutation
        return self.execute(mutation, variables)

    def delete_dtc(self, variables=None):
        mutation = Dtc_Mutation.delete_dtc_mutation
        return self.execute(mutation, variables)

    def get_dtc(self, variables=None):
        query = Dtc_Query.get_dtc_query
        return self.execute(query, variables)

    # ECU Functions:
    def get_ecu(self, variables=None):
        query = Ecu_Query.get_ecu_query
        return self.execute(query, variables)

    # Formula Functions:
    def upsert_formula(self, variables=None):
        mutation = Formula_Mutation.upsert_formula_mutation
        return self.execute(mutation, variables)

    def upsert_formula_constant(self, variables=None):
        mutation = Formula_Mutation.upsert_formula_constant_mutation
        return self.execute(mutation, variables)

    def load_formula(self, variables=None):
        query = Formula_Query.load_formula_query
        return self.execute(query, variables)

    def calculate_formula(self, variables=None):
        query = Formula_Query.calculate_formula_query
        return self.execute(query, variables)

    # GPS Functions
    def upsert_gps(self, variables=None):
        mutation = GPS_Mutation.upsert_gps_mutation
        return self.execute(mutation, variables)

    def delete_gps(self, variables=None):
        mutation = GPS_Mutation.delete_gps_mutation
        return self.execute(mutation, variables)

    def get_gps(self, variables=None):
        query = GPS_Query.get_gps_query
        return self.execute(query, variables)

    # Message Functions
    def create_message(self, variables=None):
        mutation = Message_Mutation.create_message_mutation
        return self.execute(mutation, variables)

    def get_message(self, variables=None):
        query = Message_Query.get_message_query
        return self.execute(query, variables)

    # Network Stats Functions
    def create_network_stats(self, variables=None):
        mutation = Network_Stats_Mutation.create_network_stats_mutation
        return self.execute(mutation, variables)

    def get_network_stats(self, variables=None):
        query = Network_Stats_Query.get_network_stats_query
        return self.execute(query, variables)

    # Network Functions
    def get_network(self, variables=None):
        query = Network_Query.get_network_query
        return self.execute(query, variables)

    # Signal Functions
    def upsert_signal_data(self, variables=None):
        mutation = Signals_Mutation.upsert_signal_data_mutation
        return self.execute(mutation, variables)

    def delete_signal_data(self, variables=None):
        mutation = Signals_Mutation.delete_signal_data_mutation
        return self.execute(mutation, variables)

    def get_signals(self, variables=None):
        query = Signals_Query.get_signals_query
        return self.execute(query, variables)

    def get_signal_data(self, variables=None):
        query = Signals_Query.get_signals_data_query
        return self.execute(query, variables)

    # Version Functions
    def upsert_version(self, variables=None):
        mutation = Version_Mutation.upsert_version_mutation
        return self.execute(mutation, variables)

    def delete_version(self, variables=None):
        mutation = Version_Mutation.delete_version_mutation
        return self.execute(mutation, variables)

    def get_version(self, variables=None):
        query = Version_Query.get_version_query
        return self.execute(query, variables)

    # Fail Processing Function
    def upsert_failed_processing(self, variables=None):
        mutation = FailProcessingMutation.upsert_failed_processing_mutation
        return self.execute(mutation, variables)

    def delete_failed_processing(self, variables=None):
        mutation = FailProcessingMutation.delete_failed_processing_mutation
        return self.execute(mutation, variables)

    def get_failed_processing(self, variables=None):
        query = FailProcessingQuery.get_failed_processing_query
        return self.execute(query, variables)
