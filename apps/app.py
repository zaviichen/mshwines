from oscar.app import Shop

from apps.checkout.app import application as checkout_app
from apps.catalogue.app import application as catalogue_app


class Application(Shop):
    # Use local checkout app so we can mess with the view classes
    checkout_app = checkout_app
    catalogue_app = catalogue_app


application = Application()
