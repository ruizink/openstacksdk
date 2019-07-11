# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.shared_file_system import _base_proxy
from openstack.shared_file_system.v2 import type as _type
from openstack.shared_file_system.v2 import share as _share
from openstack import resource


class Proxy(_base_proxy.BaseSharedFileSystemProxy):

    def get_type(self, type):
        """Get a single type

        :param type: The value can be the ID of a type or a
                     :class:`~openstack.shared_file_system.v2.type.Type`
                     instance.

        :returns: One :class:`~openstack.shared_file_system.v2.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_type.Type, type)

    def types(self, **query):
        """Retrieve a generator of share types

        :returns: A generator of share type objects.
        """
        return self._list(_type.Type, **query)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create a
                        :class:`~openstack.shared_file_system.v2.type.Type`,
                        comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.shared_file_system.v2.type.Type`
        """
        return self._create(_type.Type, **attrs)

    def delete_type(self, type, ignore_missing=True):
        """Delete a type

        :param type: The value can be either the ID of a type or a
                     :class:`~openstack.shared_file_system.v2.type.Type`
                     instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the type does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(_type.Type, type, ignore_missing=ignore_missing)

    def get_share(self, share):
        """Get a single share

        :param share: The value can be the ID of a share or a
                    :class:`~openstack.shared_file_system.v2.share.Share`
                    instance.

        :returns: One :class:`~openstack.shared_file_system.v2.share.Share`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_share.Share, share)

    def shares(self, details=True, **query):
        """Retrieve a generator of shares

        :param bool details: When set to ``False`` no extended attributes
            will be returned. The default, ``True``, will cause objects with
            additional attributes to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the shares being returned.  Available parameters include:

            * name: Name of the share as a string.
            * all_projects: Whether return the shares in all projects
            * status: Value of the status of the share so that you can filter
                    on "available" for example.

        :returns: A generator of share objects.
        """
        base_path = '/shares/detail' if details else None
        return self._list(_share.Share, base_path=base_path, **query)

    def create_share(self, **attrs):
        """Create a new share from attributes

        :param dict attrs: Keyword arguments which will be used to create a
                    :class:`~openstack.shared_file_system.v2.share.Share`,
                    comprised of the properties on the Share class.

        :returns: The results of share creation
        :rtype: :class:`~openstack.shared_file_system.v2.share.Share`
        """
        return self._create(_share.Share, **attrs)

    def delete_share(self, share, ignore_missing=True):
        """Delete a share

        :param share: The value can be either the ID of a share or a
                    :class:`~openstack.shared_file_system.v2.share.Share`
                    instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the share does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent share.

        :returns: ``None``
        """
        self._delete(_share.Share, share, ignore_missing=ignore_missing)

    def extend_share(self, share, size):
        """Extend a share

        :param share: The value can be either the ID of a share or
            a :class:`~openstack.shared_file_system.v2.share.Share` instance.
        :param size: New share size

        :returns: None
        """
        share = self._get_resource(_share.Share, share)
        share.extend(self, size)

    def shrink_share(self, share, size):
        """Shrink a share

        :param share: The value can be either the ID of a share or
            a :class:`~openstack.shared_file_system.v2.share.Share` instance.
        :param size: New share size

        :returns: None
        """
        share = self._get_resource(_share.Share, share)
        share.shrink(self, size)

    def wait_for_status(self, res, status='ACTIVE', failures=None,
                        interval=2, wait=120):
        """Wait for a resource to be in a particular status.

        :param res: The resource to wait on to reach the specified status.
                    The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        """
        failures = ['Error'] if failures is None else failures
        return resource.wait_for_status(
            self, res, status, failures, interval, wait)

    def wait_for_delete(self, res, interval=2, wait=120):
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait)
