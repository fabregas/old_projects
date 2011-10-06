from django.test import TestCase
from console_base.menu import get_menu
from console_base import auth, models

class MenuTest(TestCase):
    def test_menu_load(self):

        menu = get_menu()

        self.failUnlessEqual(len(menu)>0, True)
        self.failUnlessEqual(menu[0].has_key('children'), True)

    def test_01_authenticate(self):
        user = models.NmUser(name='fabregas', password_hash='26c01dbc175433723c0f3ad4d5812948', email_address='blikporject@gmail.com', additional_info='')
        user.save()
        auth.cache_users()

        try:
            auth.authenticate('fabregas', 'test')

            auth.authenticate('fabregas1', 'blik')
        except Exception, err:
            pass
        else:
            raise Exception('Should be exception in this case')

        user = auth.authenticate('fabregas', 'blik')
        self.failUnlessEqual(user.name, 'fabregas')
        self.failUnlessEqual(user.email_address, 'blikporject@gmail.com')

        #update user
        old_pwd = user.password_hash
        user.password_hash = '8977dfac2f8e04cb96e66882235f5aba' #md5 of 'changed'
        user.save()

        auth.update_user_cache(user)

        try:
            auth.authenticate('fabregas', 'blik')
        except Exception, err:
            pass
        else:
            raise Exception('Should be exception in this case')

        user = auth.authenticate('fabregas', 'changed')
        self.failUnlessEqual(user.name, 'fabregas')

        #restore default password
        user.password_hash = old_pwd
        user.save()
        auth.update_user_cache(user)

