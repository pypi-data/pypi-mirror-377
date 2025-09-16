import os
from bits_aviso_python_sdk.services.sap import SAP
from bits_aviso_python_sdk.helpers.files import write_json


def test():
    """Test the SAP class."""
    username = os.getenv('SAP_USERNAME')
    password = os.getenv('SAP_PASSWORD')
    sales_org = os.getenv('SAP_SALES_ORG')
    url = ''
    sap = SAP(username, password, url)
    write_json(sap.list_all_quotes(sales_org), 'quotes.json')


if __name__ == '__main__':
    test()
