import unittest
from blik.management.core import Session, BaseManagementAPI, auth

class MySession(Session):
    def authorize(self, role):
        if role == 'admin':
            return True
        return False

class MyAPI(BaseManagementAPI):
    @auth('admin')
    def some_method1(self, test):
        return test

    @auth('some_role')
    def some_method2(self):
        print('This code will never executed')


class TestCoreInit(unittest.TestCase):
    def test_base_mgmt_api(self):
        api = MyAPI(MySession())

        msg = 'test message'
        ret = api.some_method1(msg)
        self.assertEqual(ret, msg)

        try:
            api.some_method2()
        except Exception, err:
            pass
        else:
            raise Exception('Exception expected in this case...')


if __name__ == '__main__':
    unittest.main()
