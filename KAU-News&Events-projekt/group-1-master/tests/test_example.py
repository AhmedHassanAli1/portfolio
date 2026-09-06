import pytest, sys, os
#from web import create_app

# Fixtures can be used to create shared objects used by multiple tests
@pytest.fixture
def client():
    return 1
    #app = create_app()
    #return app.test_client()
def test_home_page():
    return 1
# All tests must start with test
# If all asserts are true, test is successful
#def test_home_page(client):
 #   response = client.get("/")
  #  assert response.status_code == 200
   # assert b"Hello World" in response.data
