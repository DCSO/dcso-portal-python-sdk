# Copyright (c) 2020, DCSO GmbH

"""
Definitions of abstract base classes used throughout the `dcso.portal` module.
"""

from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import List, Optional


class APIAbstract(metaclass=ABCMeta):
    @property
    @abstractmethod
    def api_url(self) -> str:
        raise NotImplemented

    @api_url.setter
    @abstractmethod
    def api_url(self, url: str) -> None:
        raise NotImplemented

    @property
    @abstractmethod
    def token(self) -> str:
        raise NotImplemented

    @token.setter
    @abstractmethod
    def token(self, token: str) -> None:
        raise NotImplemented

    @abstractmethod
    def execute_graphql(self, query: str,
                        variables: Optional[dict] = None,
                        fragments: Optional[List[str]] = None) -> namedtuple:
        raise NotImplemented


class ServiceAbstract(metaclass=ABCMeta):
    @property
    @abstractmethod
    def _api(self) -> APIAbstract:
        pass

    @_api.setter
    @abstractmethod
    def _api(self, url: str) -> None:
        raise NotImplemented
