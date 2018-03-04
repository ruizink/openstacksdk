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

from openstack.tests.unit import base

from openstack.block_storage import block_storage_service


class TestBlockStorageService(base.TestCase):

    def test_service(self):
        sot = block_storage_service.BlockStorageService()
        self.assertEqual("volume", sot.service_type)
        self.assertEqual("public", sot.interface)
        self.assertIsNone(sot.region)
        self.assertIsNone(sot.service_name)
        self.assertEqual(1, len(sot.valid_versions))
        self.assertEqual("v2", sot.valid_versions[0].module)
        self.assertEqual("v2", sot.valid_versions[0].path)