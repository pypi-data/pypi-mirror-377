"""
This module provides tools to interact with the SAP server. It includes methods to get quote details and list quotes from a given sales organization.

---

## Installation

To install the SAP module, use `pip`:

```sh
pip install bits_aviso_python_sdk
```

---

## Usage

### Initialization

To initialize the SAP class, you need to provide a username and password for authentication.
Optionally, you can provide the URL of the SAP server.

```python
from bits_aviso_python_sdk.services.sap import SAP

sap = SAP(username='your_username', password='your_password', url='http://sap.broadinstitute.org:8085')
```

### Examples

---

#### Get Quote Details

To get the details of a specific quote, use the `get_quote_details` method:

```python
quote_number = '12345'
quote_details, error = sap.get_quote_details(quote_number)

if error:
    print(f"Error: {error}")
else:
    print(f"Quote Details: {quote_details}")
```

---

#### List All Quotes

To list all quotes from a given sales organization, use the `list_all_quotes` method:

```python
sales_org = '1000'
quotes, error = sap.list_all_quotes(sales_org)

if error:
  print(f"Error: {error}")
else:
  print(f"Quotes: {quotes}")
```

---

## Error Handling

If an error occurs during the execution of a method,
the method will return a tuple containing `None` for the data and an error payload.

```json
{
    "Error": "An error message will be here",
    "Function": "The function that caused the error"
}
```

---
"""
import requests
import urllib3
from bits_aviso_python_sdk.helpers import convert_xml_to_dict, resolve_dns
from bits_aviso_python_sdk.services.sap.payloads import *

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


class SAP:
    def __init__(self, username, password, url, dns_resolve=False, dns_server=None):
        """
        Initialize the SAP class for interacting with the SAP server.

        Args:
            username (str): Username for authentication.
            password (str): Password for authentication.
            url (str): Base URL of the SAP server (must include protocol).
            dns_resolve (bool, optional): Whether to resolve the DNS. Defaults to False.
            dns_server (str, optional): DNS server to use. Defaults to None.
        """
        self.username = username
        self.password = password
        self.url = url
        self.dns_resolve = dns_resolve
        self.dns_server = dns_server
        self.headers = {'Content-Type': 'text/xml; charset=utf-8'}

    def api_handler(self, endpoint, payload):
        """
        Handle an API call to the SAP server.

        Args:
            endpoint (str): The endpoint to call (appended to base URL).
            payload (str): The XML payload to send to the SAP server.

        Returns:
            tuple: (response_data (dict), error_payload (dict)).
        """
        # check if the url needs to be resolved
        if self.dns_resolve:
            ip = resolve_dns(self.url, dns_server=self.dns_server)
            if not ip:
                raise ValueError(f'Unable to resolve the DNS for {self.url} with DNS server {self.dns_server}.')

            base_url = f'https://{ip}:8005'
            ssl_verify = False  # disable SSL verification when using IP address

        else:
            base_url = self.url
            ssl_verify = True

        # create the url
        url = f'{base_url}{endpoint}'

        try:
            # call the api
            response = requests.post(url, headers=self.headers, auth=(self.username, self.password), data=payload,
                                     verify=ssl_verify)

            # check the response
            if response.status_code != 200:
                raise TimeoutError(f'Unable to call the API. | Error Code {response.status_code}:'
                                   f' {response.reason}')

            else:
                # convert the xml response to json
                sap_data = convert_xml_to_dict(response.content.decode('utf-8'))
                if not isinstance(sap_data, dict):
                    return {}, {'Error': 'Failed to parse XML response to dict.'}
                return sap_data, {}

        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout, TimeoutError, ValueError) as e:
            return {}, {'Error': f'Unable to call the API. | {e}'}

    def get_quote_details(self, quote_number):
        """
        Get the details of a specific quote from the SAP server.

        Args:
            quote_number (str): The quote number.

        Returns:
            tuple: (quote_data (list of dict), error_payload (dict)).
        """
        # create the payload
        xml_str = get_quote_details(quote_number)

        # call the api
        endpoint = '/sap/bc/srt/rfc/sap/zapisdquotedetailsv3/100/zapisdquotedetailsv3service/zapisdquotedetailsv3binding'
        quote_details, quote_details_error = self.api_handler(endpoint, xml_str)

        # check the response
        if quote_details_error:  # add function name to the error payload
            quote_details_error['Function'] = 'get_quote_details'
            return [], quote_details_error

        else:
            try:
                # parse the quote details safely
                env = quote_details.get('soap-env:Envelope', {})
                body = env.get('soap-env:Body', {})
                response = body.get('n0:ZBAPISDQUOTEDETAILSV3Response', {})
                if not isinstance(response, dict):
                    raise TypeError("Expected response to be a dict, got {}".format(type(response).__name__))
                response.pop('@xmlns:n0', None)  # remove the namespace
                # move items up one level in the dict
                quote_data = self._move_up_one_level(response, nested_key='item')
                return quote_data, {}

            except (KeyError, TypeError) as e:
                quote_details_error['Function'] = 'get_quote_details'
                quote_details_error['Error'] = f'Unable to parse the quote details from the response. | {e}'
                return [], quote_details_error

    def list_all_quotes(self, sales_org):
        """
        List all quotes from a given sales organization in the SAP server.

        Args:
            sales_org (str): The sales organization to list quotes for.

        Returns:
            tuple: (quotes_data (list of dict), error_payload (dict)).
        """
        # create the payload
        xml_str = list_quotes(sales_org)

        # call the api
        endpoint = '/sap/bc/srt/rfc/sap/zapisdactivequotes/100/zapisdactivequotesservice/zapisdactivequotesbinding'
        quotes, quotes_error = self.api_handler(endpoint, xml_str)

        # check the response
        if quotes_error:
            quotes_error['Function'] = 'list_all_quotes'
            return [], quotes_error

        else:
            try:
                # Ensure quotes is a dict and traverse safely
                if not isinstance(quotes, dict):
                    raise TypeError("Expected 'quotes' to be a dict, got {}".format(type(quotes).__name__))
                env = quotes.get('soap-env:Envelope', {})
                body = env.get('soap-env:Body', {})
                response = body.get('n0:ZbapisdactivequotesResponse', {})
                new_quotation_list = response.get('Newquotationlistd', {})
                quotes_data = new_quotation_list.get('item', [])
                return quotes_data, {}

            except (KeyError, TypeError) as e:
                quotes_error['Function'] = 'list_all_quotes'
                quotes_error['Error'] = f'Unable to parse the quotes from the response. | {e}'
                return [], quotes_error

    @staticmethod
    def _move_up_one_level(data, nested_key='item'):
        """
        Move nested data up one level in a dictionary.

        Args:
            data (dict): The data to consolidate.
            nested_key (str, optional): The key to use as the dictionary key. Defaults to 'item'.

        Returns:
            dict: The refactored data with nested items moved up one level.
        """
        for key, value in data.items():
            if isinstance(value, list) or isinstance(value, dict):
                if nested_key in value:
                    data[key] = data[key].pop(nested_key)

        return data
