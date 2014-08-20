from django.conf import settings
from django.views.generic import ListView
from oscar.core.loading import get_model
import datetime

Product = get_model('catalogue', 'product')
ProductRecord = get_model('analytics', 'ProductRecord')


class ProductRecordView(ListView):
    """
    Browse products in a given category
    """
    context_object_name = "products"
    template_name = 'status/browse.html'
    paginate_by = None
    record_size = settings.OSCAR_PRODUCTS_PER_PAGE
    enforce_paths = True

    def get_ranks(self):
        records = ProductRecord.objects.order_by('-num_views')[:self.record_size]
        return [e.product_id for e in records]

    def get_context_data(self, **kwargs):
        context = super(ProductRecordView, self).get_context_data(**kwargs)
        id_map = {e.id: e for e in context['products']}
        context['products'] = []
        for id in self.ranks:
            if id in id_map:
                context['products'].append(id_map[id])
        context['title'] = 'Most Popular'
        return context

    def get_queryset(self):
        qs = Product.browsable.base_queryset()
        self.ranks = self.get_ranks()
        if len(self.ranks) > 0:
            qs = qs.filter(id__in=self.ranks)
        return qs


class RecentProductView(ListView):
    """
    Browse the new arrival products
    """
    context_object_name = "products"
    template_name = 'status/browse.html'
    paginate_by = settings.OSCAR_PRODUCTS_PER_PAGE
    enforce_paths = True

    def get_context_data(self, **kwargs):
        context = super(RecentProductView, self).get_context_data(**kwargs)
        context['title'] = 'New Arrivals'
        return context

    def get_queryset(self):
        qs = Product.browsable.base_queryset()
        dt = datetime.date.today() - datetime.timedelta(days=30)
        qs = qs.filter(date_created__gte=dt).order_by('-images', '-stockrecords', '-date_created')
        return qs
