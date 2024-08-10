import logging

from etl.backoff import backoff
from .redis_state_storage import State


class StateETL:
    def __init__(self, state: State):
        self.state = state

    @backoff(limit_of_retries=10)
    def get_last_state(self, table_name: str) -> str:
        """
        Method gets last modified time.
        :param table_name: The name of DB table.
        :return: Last modified time in string format.
        """
        # Get last modified datetime.
        state_modified = self.state.get_state(f"{table_name}")

        # Set date if state doesn't exist.
        if state_modified:
            logging.info("State received successfully. The ETL process continues.")
        else:
            state_modified = "1800-01-01"
            self.state.set_state(f"{table_name}", state_modified)
            logging.info(f"There is no state for {table_name} ETL process. State was successfully created. The ETL "
                         f"process begins.")

        return state_modified

    @backoff(limit_of_retries=10)
    def set_last_state(self, table_name: str, last_modified: str) -> None:
        """
        Method sets last modified time of entry in the batch data from DB.
        :param table_name: The name of DB table.
        :param last_modified: Last modified time of entry in the batch data from DB.
        :return: None
        """
        self.state.set_state(f"{table_name}", last_modified)

    @backoff(limit_of_retries=10)
    def reset_state(self) -> None:
        """
        Method resets all states.
        :return: None
        """
        self.state.set_state('film_work', "1800-01-01")
        self.state.set_state('genre', "1800-01-01")
        self.state.set_state('person', "1800-01-01")
