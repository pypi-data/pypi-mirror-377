import os
from requests import exceptions
from kbcstorage.configurations import Configurations
from tests.base_test_case import BaseTestCase


class TestEndpoint(BaseTestCase):
    def setUp(self):
        self.configurations = Configurations(os.getenv('KBC_TEST_API_URL'), os.getenv('KBC_TEST_TOKEN'), 'default')

    def tearDown(self):
        try:
            for configuration in self.configurations.list(self.TEST_COMPONENT_NAME):
                self.configurations.delete(self.TEST_COMPONENT_NAME, configuration['id'])
        except exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise

    def testCreateConfiguration(self):
        configuration = self.configurations.create(self.TEST_COMPONENT_NAME, 'test_create_configuration')
        self.assertTrue('id' in configuration)
        self.assertTrue('name' in configuration)
        self.assertTrue('description' in configuration)
        self.assertTrue('configuration' in configuration)

    def testDeleteConfiguration(self):
        configuration = self.configurations.create(self.TEST_COMPONENT_NAME, 'test_delete_configuration')
        configuration = self.configurations.detail(self.TEST_COMPONENT_NAME, configuration['id'])
        self.assertTrue('id' in configuration)
        self.assertTrue('name' in configuration)
        self.assertEqual(configuration['name'], 'test_delete_configuration')
        self.assertTrue('description' in configuration)
        self.assertTrue('configuration' in configuration)

        self.configurations.delete(self.TEST_COMPONENT_NAME, configuration['id'])
        with self.assertRaises(exceptions.HTTPError):
            self.configurations.detail(self.TEST_COMPONENT_NAME, configuration['id'])

    def testListConfigurations(self):
        self.configurations.create(self.TEST_COMPONENT_NAME, 'test_list_configurations')
        configurations = self.configurations.list(self.TEST_COMPONENT_NAME)
        self.assertTrue(len(configurations) > 0)
        for configuration in configurations:
            with self.subTest():
                self.assertTrue('id' in configuration)
                self.assertTrue('name' in configuration)
                self.assertTrue('description' in configuration)
                self.assertTrue('configuration' in configuration)

        with self.subTest():
            with self.assertRaises(exceptions.HTTPError):
                configurations = self.configurations.list('non-existent-component')

    def testConfigurationMetadata(self):
        self.configurations.create(
            component_id=self.TEST_COMPONENT_NAME,
            configuration_id='test_configuration_metadata',
            name='test_configuration_metadata',
        )
        metadataPayload = [
            {
                'key': 'testConfigurationMetadata',
                'value': 'success',
            }
        ]
        metadataList = self.configurations.metadata.create(
            component_id=self.TEST_COMPONENT_NAME,
            configuration_id='test_configuration_metadata',
            provider='test',
            metadata=metadataPayload,
        )

        with (self.subTest('assert metadata create response')):
            self.assertEqual(1, len(metadataList))
            metadataItem = metadataList[0]
            self.assertTrue('id' in metadataItem)
            # self.assertTrue('provider' in metadata) not yet
            self.assertTrue('key' in metadataItem)
            self.assertTrue('value' in metadataItem)

            metadataList = self.configurations.metadata.list(
                component_id=self.TEST_COMPONENT_NAME,
                configuration_id='test_configuration_metadata'
            )

        with (self.subTest('assert metadata list response')):
            self.assertTrue(len(metadataList) > 0)
            for metadataList in metadataList:
                self.assertTrue('id' in metadataList)
                # self.assertTrue('provider' in metadata) not yet
                self.assertTrue('key' in metadataList)
                self.assertTrue('value' in metadataList)

        self.configurations.metadata.delete(
            component_id=self.TEST_COMPONENT_NAME,
            configuration_id='test_configuration_metadata',
            metadata_id=metadataList['id']
        )
        metadataList = self.configurations.metadata.list(
            component_id=self.TEST_COMPONENT_NAME,
            configuration_id='test_configuration_metadata'
        )

        with (self.subTest('assert metadata delete means metadata no longer in list')):
            self.assertTrue(len(metadataList) == 0)
