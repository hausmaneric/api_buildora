import unittest

from source.core.system.utils import process_error_message, success_message


class CoreUtilsMessageTests(unittest.TestCase):
    def test_success_message_create(self):
        self.assertEqual(success_message('Conta', 'create'), 'Conta cadastrado com sucesso')

    def test_success_message_bootstrap(self):
        self.assertEqual(success_message('Bootstrap master', 'bootstrap'), 'Bootstrap master executado com sucesso')

    def test_process_error_message_update(self):
        self.assertEqual(process_error_message('obra', 'update'), 'Falha no processo de atualizacao de obra')

    def test_process_error_message_default(self):
        self.assertEqual(process_error_message('registro', 'unknown'), 'Falha no processo de registro')


if __name__ == '__main__':
    unittest.main()
