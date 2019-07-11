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

from openstack import resource
from openstack import utils


class Share(resource.Resource):
    resource_key = "share"
    resources_key = "shares"
    base_path = "/shares"

    _query_mapping = resource.QueryParameters(
        'name', 'status', 'project_id', all_projects='all_tenants')

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: A ID representing this share.
    id = resource.Body("id")
    #: The name of this share.
    name = resource.Body("name")
    #: A list of links associated with this share. *Type: list*
    links = resource.Body("links", type=list)

    #: The availability zone.
    availability_zone = resource.Body("availability_zone")
    #: The share description.
    description = resource.Body("description")
    #: To create a share from an existing snapshot, specify the ID of
    #: the existing share snapshot. If specified, the share is created
    #: in same availability zone and with same size of the snapshot.
    snapshot_id = resource.Body("snapshot_id")
    #: The size of the share, in GBs. *Type: int*
    size = resource.Body("size", type=int)
    #: The name of the associated share type.
    share_type_name = resource.Body("share_type_name")
    #: The name of the associated share protocol
    share_proto = resource.Body("share_proto")
    #: One or more metadata key and value pairs to associate with the share.
    metadata = resource.Body("metadata")

    #: One of the following values: creating, available, attaching, in-use
    #: deleting, error, error_deleting, backing-up, restoring-backup,
    #: error_restoring. For details on these statuses, see the
    #: Block Storage API documentation.
    status = resource.Body("status")
    #: The timestamp of this share creation.
    created_at = resource.Body("created_at")

    #: The share's current back-end.
    host = resource.Body("host")
    #: The project ID associated with current back-end.
    project_id = resource.Body("project_id")

    def _action(self, session, body):
        """Preform share actions given the message body."""
        # NOTE: This is using share.base_path instead of self.base_path
        # as both Share and ShareDetail instances can be acted on, but
        # the URL used is sans any additional /detail/ part.
        url = utils.urljoin(Share.base_path, self.id, 'action')
        headers = {'Accept': ''}
        return session.post(url, json=body, headers=headers)

    def extend(self, session, size):
        """Extend a share size."""
        body = {'os-extend': {'new_size': size}}
        self._action(session, body)

    def shrink(self, session, size):
        """Shrink a share size."""
        body = {'os-shrink': {'new_size': size}}
        self._action(session, body)


ShareDetail = Share
