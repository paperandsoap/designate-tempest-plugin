# Copyright 2016 NEC Corporation.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging
from tempest import test
from tempest.lib import exceptions as lib_exc

from designate_tempest_plugin.tests import base

LOG = logging.getLogger(__name__)


class BaseZoneExportsTest(base.BaseDnsV2Test):
    excluded_keys = ['created_at', 'updated_at', 'version', 'links',
                     'status', 'location']


class ZonesExportTest(BaseZoneExportsTest):
    @classmethod
    def setup_clients(cls):
        super(ZonesExportTest, cls).setup_clients()

        cls.zone_client = cls.os.zones_client
        cls.client = cls.os.zone_exports_client

    @test.attr(type='smoke')
    @test.idempotent_id('2dd8a9a0-98a2-4bf6-bb51-286583b30f40')
    def test_create_zone_export(self):
        LOG.info('Create a zone')
        _, zone = self.zone_client.create_zone()
        self.addCleanup(self.zone_client.delete_zone, zone['id'])

        LOG.info('Create a zone export')
        _, zone_export = self.client.create_zone_export(zone['id'])

        LOG.info('Ensure we respond with PENDING')
        self.assertEqual('PENDING', zone_export['status'])

    @test.attr(type='smoke')
    @test.idempotent_id('2d29a2a9-1941-4b7e-9d8a-ad6c2140ea68')
    def test_show_zone_export(self):
        LOG.info('Create a zone')
        _, zone = self.zone_client.create_zone()
        self.addCleanup(self.zone_client.delete_zone, zone['id'])

        LOG.info('Create a zone export')
        resp, zone_export = self.client.create_zone_export(zone['id'])

        LOG.info('Re-Fetch the zone export records')
        _, body = self.client.show_zone_export_records(str(zone_export['id']))

        LOG.info('Ensure the fetched response matches the records of '
                 'exported zone')
        self.assertExpected(zone_export, body, self.excluded_keys)

    @test.attr(type='smoke')
    @test.idempotent_id('97234f00-8bcb-43f8-84dd-874f8bc4a80e')
    def test_delete_zone_export(self):
        LOG.info('Create a zone')
        _, zone = self.zone_client.create_zone()
        self.addCleanup(self.zone_client.delete_zone, zone['id'],
                        ignore_errors=lib_exc.NotFound)

        LOG.info('Create a zone export')
        _, zone_export = self.client.create_zone_export(zone['id'])

        LOG.info('Delete the exported zone')
        _, body = self.client.delete_zone_export(zone_export['id'])

        LOG.info('Ensure the exported zone has been successfully deleted')
        self.assertRaises(lib_exc.NotFound,
            lambda: self.client.show_zone_export_records(zone_export['id']))

    @test.attr(type='smoke')
    @test.idempotent_id('476bfdfe-58c8-46e2-b376-8403c0fff440')
    def test_list_zones_exports(self):
        LOG.info('Create a zone')
        _, zone = self.zone_client.create_zone()
        self.addCleanup(self.zone_client.delete_zone, zone['id'])

        _, export = self.client.create_zone_export(zone['id'])

        LOG.info('List zones exports')
        _, body = self.client.list_zones_exports()

        self.assertGreater(len(body['exports']), 0)
