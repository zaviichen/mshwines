from django.utils.http import urlquote
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class, get_model

Product = get_model('catalogue', 'product')
ProductReview = get_model('reviews', 'ProductReview')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')


class ProductCategoryView(ListView):
    """
    Browse products in a given category
    Override the oscar's catalogue reviews, use our own rank method.
    """
    context_object_name = "products"
    template_name = 'catalogue/browse.html'
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE
    enforce_paths = True

    def get_object(self):
        if 'pk' in self.kwargs:
            # Usual way to reach a category page. We just look at the primary
            # key in case the slug changed. If it did, get() will redirect
            # appropriately
            self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        elif 'category_slug' in self.kwargs:
            # For SEO reasons, we allow chopping off bits of the URL. If that
            # happened, no primary key will be available.
            self.category = get_object_or_404(
                Category, slug=self.kwargs['category_slug'])
        else:
            # If neither slug nor primary key are given, we show all products
            self.category = None

    def get(self, request, *args, **kwargs):
        self.get_object()
        redirect = self.redirect_if_necessary(request.path, self.category)
        if redirect is not None:
            return redirect
        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths and self.category is not None:
            # Categories are fetched by primary key to allow slug changes.
            # If the slug has indeed changed, issue a redirect.
            expected_path = self.category.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_categories(self):
        """
        Return a list of the current category and it's ancestors
        """
        return list(self.category.get_descendants()) + [self.category]

    def get_summary(self):
        """
        Summary to be shown in template
        """
        return self.category.name if self.category else _('All products')

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['summary'] = self.get_summary()
        print len(context['products'])
        return context

    def get_queryset(self):
        """
        It will depress the product which doesn't have image or is unavailable.
        """
        qs = Product.browsable.base_queryset()
        if self.category is not None:
            categories = self.get_categories()
            qs = qs.filter(categories__in=categories).distinct()
        qs = qs.order_by('-images', '-stockrecords')
        return qs
