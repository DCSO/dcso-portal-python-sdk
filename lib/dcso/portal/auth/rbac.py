# Copyright (c) 2020, DCSO GmbH

from typing import Optional, Sequence

from ..abstracts import ServiceAbstract
from ..exceptions import PortalAPIResponse, PortalException
from ..util.graphql import GraphQLRequest


class Permission:
    def __init__(self, id: str, slug: str, service: str):
        self.id: str = id
        self.slug: str = slug
        self.service: str = service


class ServicePermissions:
    def __init__(self, graphql_response: Optional[dict]):
        self._permissions: Sequence[Permission] = []
        self._index_services: dict = {}
        self._index_permissions_by_id: dict = {}
        self._index_permissions_by_slug: dict = {}

        if graphql_response:
            self._handle_graphql_response(graphql_response)

    def _handle_graphql_response(self, res: dict) -> None:
        self._permissions = []  # reset
        self._index_services = {}

        idx = 0  # permissions are indexed in dicts for membership testing
        try:
            for entry in res['accessControl']['servicePermissions']:
                service = entry['service']['code']

                for p in entry['permissions']:
                    self._permissions.append(Permission(id=p['id'], slug=p['slug'], service=service))
                    self._index_services.setdefault(service, [])

                    # store the index to the permission
                    self._index_services[service].append(idx)
                    self._index_permissions_by_id[p['id']] = idx
                    self._index_permissions_by_slug[p['slug']] = idx
                    idx += 1
        except KeyError as exc:
            raise PortalAPIResponse(f"failed handling service permission ({exc})")

    def __iter__(self) -> Permission:
        for perm in self._permissions:
            yield perm

    def have(self, p) -> bool:
        """Returns True whether permission is available

        The p argument can be either the ID (a UUID) or the Slug of the permission.

        Note that the list of permissions being checked might be less than the
        permissions the user actually has. This is because only a subset can
        be queried for.

        :param p: ID (UUID) or Slug of the permission to check
        :return: True if permission is available
        """
        return p in self._index_permissions_by_slug or p in self._index_permissions_by_id

    def slugs(self) -> Sequence[str]:
        """Returns sequence of permissions' ID and Slug

        :return: Sequence of IDs and Slugs of all permissions for this service.
        """

    def as_slug_dict(self) -> dict:
        """Returns permission slugs for all services as dict

        :return: Dictionary with key the service code, and value sequence of permission slugs.
        """
        result = {}
        for p in self._permissions:
            try:
                result[p.service].append(p.slug)
            except KeyError:
                result[p.service] = [p.slug]

        return result


class RBACMixin(ServiceAbstract):
    _api = None  # mixed in

    def user_service_permissions(self, user_id: Optional[str] = None,
                                 services: Optional[Sequence[str]] = None) -> ServicePermissions:
        """Retrieves permissions available to user with ID `user_id`. The result is an instance
        of `ServicePermissions` which holds the user's permission for all or for selected services.

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        variables = {
            "id": user_id,
            "services": services
        }

        request = GraphQLRequest(api_url=self._api.api_url, token=self._api.token,
                                 query=_GRAPHQL_QUERY_USER_SERVICE_PERMISSIONS, variables=variables)

        try:
            response = request.execute_dict()
        except PortalException:
            raise

        try:
            return ServicePermissions(graphql_response=response['data']['user'])
        except PortalAPIResponse:
            raise


_GRAPHQL_QUERY_USER_SERVICE_PERMISSIONS = """
query ($id: ID, $services: [String!]) {
  user: auth_user(id: $id) {
    accessControl {
      servicePermissions(filter: {serviceCode: $services}) {
        service { code }
        permissions { id slug }
      }
    }
  }
}
"""
