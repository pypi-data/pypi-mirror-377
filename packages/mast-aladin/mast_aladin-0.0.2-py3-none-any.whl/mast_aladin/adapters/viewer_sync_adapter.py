from abc import ABC, abstractmethod


class ViewerSyncAdapter(ABC):
    @abstractmethod
    def sync_to(self, sync_viewer):
        raise NotImplementedError

    @abstractmethod
    def add_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def remove_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def show(self):
        raise NotImplementedError
