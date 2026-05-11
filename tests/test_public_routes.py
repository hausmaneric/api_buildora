import json
import unittest

try:
    from source.app import app
    APP_IMPORT_ERROR = None
except Exception as exc:
    app = None
    APP_IMPORT_ERROR = exc


@unittest.skipIf(APP_IMPORT_ERROR is not None, f'Runtime dependencies not available: {APP_IMPORT_ERROR}')
class PublicRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data.decode('utf-8'))
        self.assertTrue(payload['status'])
        self.assertEqual(payload['message'], 'API ativa')
        self.assertIn('name', payload['data'])

    def test_routes_catalog_endpoint(self):
        response = self.client.get('/api/v1/routes')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data.decode('utf-8'))
        self.assertTrue(payload['status'])
        self.assertIn('routes', payload['data'])
        self.assertGreater(payload['data']['total_routes'], 0)

    def test_smoke_plan_endpoint(self):
        response = self.client.get('/api/v1/smoke-plan')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data.decode('utf-8'))
        self.assertTrue(payload['status'])
        self.assertIn('steps', payload['data'])
        self.assertGreaterEqual(len(payload['data']['steps']), 5)

    def test_environment_endpoint(self):
        response = self.client.get('/api/v1/environment')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data.decode('utf-8'))
        self.assertTrue(payload['status'])
        self.assertIn('database', payload['data'])
        self.assertIn('validation', payload['data']['database'])

    def test_security_check_endpoint(self):
        response = self.client.get('/api/v1/security-check')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data.decode('utf-8'))
        self.assertTrue(payload['status'])
        self.assertIn('checks', payload['data'])
        self.assertIn('warnings', payload['data'])


if __name__ == '__main__':
    unittest.main()
