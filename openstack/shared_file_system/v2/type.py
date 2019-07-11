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


class Type(resource.Resource):
    resource_key = "share_type"
    resources_key = "share_types"
    base_path = "/types"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters("is_public")

    # Properties
    #: A ID representing this type.
    id = resource.Body("id")
    #: Name of the type.
    name = resource.Body("name")
    #: A dict of extra specifications. "capabilities" is a usual key.
    extra_specs = resource.Body("extra_specs", type=dict)
    #: a private share-type. *Type: bool*
    is_public = resource.Body('os-share-type-access:is_public', type=bool)

    def _action(self, session, body):
        """Preform share type actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        headers = {'Accept': ''}
        return session.post(url, json=body, headers=headers)
