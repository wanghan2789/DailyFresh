from haystack import indexes
from apps.goods.models import GoodsSKU


#model_name + Index
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    #use_template -> which file could be search
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):

        return GoodsSKU


    def index_queryset(self, using=None):
        return self.get_model().objects.all()