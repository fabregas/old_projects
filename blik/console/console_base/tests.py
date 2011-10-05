from django.test import TestCase
from console_base.menu import get_menu

class MenuTest(TestCase):
    def test_menu_load(self):

        menu = get_menu()

        self.failUnlessEqual(len(menu)>0, True)
        self.failUnlessEqual(menu[0].has_key('children'), True)

        print menu
