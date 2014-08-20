from oscar.apps.catalogue import app

from apps.catalogue import views


class CatalogueApplication(app.CatalogueApplication):
    # Replace the payment details view with our own
    category_view = views.ProductCategoryView


application = CatalogueApplication()