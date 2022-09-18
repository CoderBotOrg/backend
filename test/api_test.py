import schemathesis

schema = schemathesis.from_uri("http://192.168.1.14:8090/api/v1/openapi.json")

@schema.parametrize()
def test_api(case):
    case.call_and_validate()
