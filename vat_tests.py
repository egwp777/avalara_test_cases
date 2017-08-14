# ~*~ coding: utf-8 ~*~
import time

from requests import request
from unittest import TestCase


class TestAvalaraVATIntegration(TestCase):

    def setUp(self):
        self.avalara_sandbox = 'https://development.avalara.net/1.0/'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic [redacted]',
            'Accept': 'application/json',
            'Host': 'development.avalara.net'
        }

    def tearDown(self):
        time.sleep(3)

    def test_avalara_get_tax(self):
        data = None
        resource = 'tax/get'
        with open('./post_create_transaction_v1.json', 'r') as js:
            data = js.read()

        response = self._make_request('POST', resource, data)
        json_payload = response.json()

        self.assertEquals(200, response.status_code)
        self.assertEquals('Success', json_payload.get('ResultCode'))
        self.assertEquals('0', json_payload.get('TotalTaxable'))
        self.assertEquals('10', json_payload.get('TotalExemption'))
        self.assertEquals('10', json_payload.get('TotalAmount'))

    def test_avalara_vat_misspelled_bino(self):
        data = None
        resource = 'tax/get'
        with open('./post_create_transaction_1_misspelled.json', 'r') as js:
            data = js.read()

        response = self._make_request('POST', resource, data)

        self.assertEquals(400, response.status_code)
        self.assertIn("Malformed JSON near 'BusinessIdentificationNom'",
                      response.json().get('Messages')[0].get('Summary'))

    # GB999 9999 73
    def test_avalara_vat_with_gb_vat_id(self):
        data = None
        resource = 'tax/get'
        with open('./post_create_transaction_1_valid.json', 'r') as js:
            data = js.read()

        response = self._make_request('POST', resource, data)
        json_payload = response.json()

        self.assertEquals(200, response.status_code)
        self.assertEquals("0", json_payload.get('TotalTaxable'))
        self.assertEquals("Success", json_payload.get('ResultCode'))
        self.assertEquals("0", json_payload.get('TotalTaxCalculated'))
        self.assertEquals("10", json_payload.get('TotalExemption'))

    def test_avalara_with_bino_and_uk_address(self):
        data = None
        resource = 'tax/get'
        with open('./post_create_transaction_1_failed_500.json', 'r') as js:
            data = js.read()

        response = self._make_request('POST', resource, data)
        json_payload = response.json()

        self.assertEquals(
            'GB VAT',
            json_payload
            .get('TaxLines', [])[0].get('TaxDetails', [])[0].get('TaxName'))
        self.assertEquals('0', json_payload.get('TotalTaxable'))
        self.assertEquals('0', json_payload.get('TotalTaxCalculated'))
        self.assertEquals('10', json_payload.get('TotalExemption'))
        self.assertEquals('10', json_payload.get('TotalAmount'))

    def _make_request(self, method_type, resource, data):
        """ Centralize wrapper for requests.request.
            :param method_type: string
            :param resource: string
            :param data: dict
            :return: ResponseObject
            :raises: None
        """
        response = request(method_type,
                           '{}{}'.format(self.avalara_sandbox, resource),
                           data=data,
                           headers=self.headers)
        return response
