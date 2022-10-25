import logging

from brownie import network


class NetworkSwitcher(object):
    def __init__(self, network_name: str, return_to_original: bool = True) -> None:
        self.previous_network = network.show_active()
        self.new_network = network_name
        self.return_to_original = return_to_original

    def __enter__(self):
        if self.new_network != self.previous_network:
            logging.debug(f"Switching to {self.new_network}")
            network.disconnect()
            network.connect(self.new_network)

    def __exit__(self, type, value, traceback):
        if self.return_to_original and self.new_network != self.previous_network:
            logging.debug(f"Switching back to {self.previous_network}")
            network.disconnect()
            network.connect(self.previous_network)
