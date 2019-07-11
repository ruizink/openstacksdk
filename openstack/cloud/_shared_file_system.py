# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa
import warnings

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import proxy
from openstack import utils


def _no_pending_shares(shares):
    """If there are any shares not in a steady state, don't cache"""
    for share in shares:
        if share['status'] not in ('available', 'error'):
            return False
    return True


class SharedFileSystemCloudMixin(_normalize.Normalizer):

    @property
    def _share_client(self):
        if 'share' not in self._raw_clients:
            client = self._get_raw_client('share')
            self._raw_clients['share'] = client
        return self._raw_clients['share']

    @_utils.cache_on_arguments(should_cache_fn=_no_pending_shares)
    def list_shares(self):
        """List all available shares.

        :returns: A list of shares ``munch.Munch``.

        """
        def _list(data):
            shares.extend(data.get('shares', []))
            endpoint = None
            for l in data.get('shares_links', []):
                if 'rel' in l and 'next' == l['rel']:
                    endpoint = l['href']
                    break
            if endpoint:
                try:
                    _list(self._share_client.get(endpoint))
                except exc.OpenStackCloudURINotFound:
                    # Catch and re-raise here because we are making recursive
                    # calls and we just have context for the log here
                    self.log.debug(
                        "While listing shares, could not find next link"
                        " {link}.".format(link=data))
                    raise

        # Fetching paginated shares can fails for several reasons, if
        # something goes wrong we'll have to start fetching shares from
        # scratch
        attempts = 5
        for _ in range(attempts):
            shares = []
            data = self._share_client.get('/shares/detail')
            if 'shares_links' not in data:
                # no pagination needed
                shares.extend(data.get('shares', []))
                break

            try:
                _list(data)
                break
            except exc.OpenStackCloudURINotFound:
                pass
        else:
            self.log.debug(
                "List shares failed to retrieve all shares after"
                " {attempts} attempts. Returning what we found.".format(
                    attempts=attempts))
        # list shares didn't complete succesfully so just return what
        # we found
        return self._normalize_shares(
            self._get_and_munchify(key=None, data=shares))

    @_utils.cache_on_arguments()
    def list_share_types(self, get_extra=True):
        """List all available share types.

        :param get_extra: Whether or not to fetch extra specs for each flavor.
                          Defaults to True. Default behavior value can be
                          overridden in clouds.yaml by setting
                          shade.get_extra_specs to False.

        :returns: A list of share types ``munch.Munch``.

        """
        data = self._share_client.get(
            '/types',
            params=dict(is_public='all'),
            error_message='Error fetching share_type list')
        return self._get_and_munchify('share_types', data)

    def get_share(self, name_or_id=None, filters=None):
        """Get an aggregate by name or ID.

        :param name_or_id: Name or ID of the aggregate.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: An share dict or None if no matching share is
                  found.

        """
        return _utils._get_entity(self, 'share', name_or_id, filters)

    def get_share_by_id(self, id):
        """ Get a share by ID

        :param id: ID of the share.
        :returns: A share ``munch.Munch``.
        """
        data = self._share_client.get(
            '/shares/{id}'.format(id=id),
            error_message="Error getting share type with ID {id}".format(id=id)
        )

        share = self._get_and_munchify('share', data)

        return share

    def get_share_type(self, name_or_id, filters=None):
        """Get a share type by name or ID.

        :param name_or_id: Name or ID of the share type.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A share type ``munch.Munch`` or None if no matching share
                  type is found.

        """
        return _utils._get_entity(self, 'share_type', name_or_id, filters)

    def create_share(self, share_proto, size, wait=True, timeout=None,
                     **kwargs):
        """Create a new share.
        :param share_proto: Protocol for the share to be created.
        :param size: Size, in GB of the share to create.
        :param name: (optional) Name for the share.
        :param description: (optional) Description for the share.
        :param wait: If true, waits for share to be created.
        :param timeout: Seconds to wait for share creation. None is forever.
        :param kwargs: Keyword arguments as expected for manila client.

        :returns: a dict representing the new share.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """
        kwargs['share_proto'] = share_proto
        kwargs['size'] = size
        payload = dict(share=kwargs)
        data = self._share_client.post(
            '/shares',
            json=dict(payload),
            error_message='Error in creating share')
        share = self._normalize_share(self._get_and_munchify('share', data))
        self.list_shares.invalidate(self)

        if share['status'] == 'error':
            raise exc.OpenStackCloudException("Error in creating share")

        if wait:
            share_id = share['id']
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the share to be available."):
                share = self.get_share(share_id)

                if not share:
                    continue

                if share['status'] == 'available':
                    return share

                if share['status'] == 'error':
                    raise exc.OpenStackCloudException("Error in creating share")

        return self._normalize_share(share)

    def update_share(self, name_or_id=None, display_name=None,
                     display_description=None, is_public=None):
        """Update a share.
        :param name_or_id: Name or ID of share being updated.
        :param name: New share name
        :param availability_zone: Availability zone to assign to hosts
        :returns: a dict representing the updated share.
        :raises: OpenStackCloudException on operation error.
        """
        share = self.get_share(name_or_id)
        if not share:
            raise exc.OpenStackCloudException(
                "Share %s not found." % name_or_id)

        share_ref = {}
        if display_name:
            share_ref['display_name'] = display_name
        if display_description:
            share_ref['display_description'] = display_description
        if is_public:
            share_ref['is_public'] = is_public

        data = self._share_client.put(
            '/shares/{id}'.format(id=share['id']),
            json={'share': share_ref},
            error_message="Error updating share {name}".format(
                name=name_or_id))

        return self._get_and_munchify('share', data)

    def delete_share(self, name_or_id=None, wait=True, timeout=None,
                     force=False):
        """Delete a share.

        :param name_or_id: Name or unique ID of the share.
        :param wait: If true, waits for share to be deleted.
        :param timeout: Seconds to wait for share deletion. None is forever.
        :param force: Force delete share even if the share is in deleting
            or error_deleting state.

        :raises: OpenStackCloudTimeout if wait time exceeded.
        :raises: OpenStackCloudException on operation error.
        """

        self.list_shares.invalidate(self)
        share = self.get_share(name_or_id)

        if not share:
            self.log.debug(
                "Share %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True)
            return False

        with _utils.shade_exceptions("Error in deleting share"):
            try:
                if force:
                    # TODO(santosm): handle microversions
                    # If API version 1.0-2.6 is used then all share actions,
                    # defined below, should include prefix os- in top element
                    # of request JSON's body.
                    # For example: {"access_list": null} is valid for v2.7+.
                    # And {"os- access_list": null} is valid for v1.0-2.6
                    self._share_client.post(
                        'shares/{id}/action'.format(id=share['id']),
                        json={'os-force_delete': None})
                else:
                    self._share_client.delete(
                        'shares/{id}'.format(id=share['id']))
            except exc.OpenStackCloudURINotFound:
                self.log.debug(
                    "Share {id} not found when deleting. Ignoring.".format(
                        id=share['id']))
                return False

        self.list_shares.invalidate(self)
        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for the share to be deleted."):

                if not self.get_share(share['id']):
                    break

        return True

    def get_share_id(self, name_or_id):
        share = self.get_share(name_or_id)
        if share:
            return share['id']
        return None

    def share_exists(self, name_or_id):
        return self.get_share(name_or_id) is not None

    def search_shares(self, name_or_id=None, filters=None):
        shares = self.list_shares()
        return _utils._filter_list(
            shares, name_or_id, filters)

    def search_share_types(
            self, name_or_id=None, filters=None, get_extra=True):
        share_types = self.list_share_types(get_extra=get_extra)
        return _utils._filter_list(share_types, name_or_id, filters)
