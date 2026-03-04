from http import HTTPStatus

RULE_DATA = dict(
    method='GET',
    url='test_url/api/api_v1/id',
    call_backend=False,
    status_code=HTTPStatus.OK,
    response="""{'response': 'test response'}""",
)
