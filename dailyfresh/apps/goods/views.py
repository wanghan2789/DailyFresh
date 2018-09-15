from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.cache import cache
from apps.goods.models import GoodsType,GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection
from apps.order.models import OrderGoods
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
# Create your views here.

class IndexView(View):
    def get(self,request):
        #load in cache
        context = cache.get('index_page_data')
        if context is None:
            print('set cache')
            #the empty you should do a cache


            types = GoodsType.objects.all()

            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # type_goods_banners = IndexTypeGoodsBanner.objects.all()
            for type in types:
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                type.image_banners = image_banners
                type.title_banners = title_banners

            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners}

            cache.set('index_page_data', context, 3600)



        #-----------------------------------------------
        #until here you must save all date in your cache
        #-----------------------------------------------


        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # the user aready login
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # context = {'types': types,
        #            'goods_banners': goods_banners,
        #            'promotion_banners': promotion_banners,
        #            #'type_goods_banners':type_goods_banners,
        #            'cart_count': cart_count}
        context.update(cart_count = cart_count)

        return render(request, 'index.html',context)


class DetailView(View):
    def get(self, request, goods_id):

        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))


        types = GoodsType.objects.all()

        #if command == null this is a bad data should del
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        #order by time
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]


        #same type commend
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)


        user = request.user
        cart_count = 0
        if user.is_authenticated():

            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)


            conn = get_redis_connection('default')
            history_key = 'history_%d'%user.id

            conn.lrem(history_key, 0, goods_id)

            conn.lpush(history_key, goods_id)

            conn.ltrim(history_key, 0, 4)


        context = {'sku':sku, 'types':types,
                   'sku_orders':sku_orders,
                   'new_skus':new_skus,
                   'same_spu_skus':same_spu_skus,
                   'cart_count':cart_count}


        return render(request, 'detail.html', context)


class ListView(View):

    def get(self, request, type_id, page):
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))


        types = GoodsType.objects.all()

        # sort=default  by  id
        # sort=price
        # sort=hot
        sort = request.GET.get('sort')

        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')


        paginator = Paginator(skus, 1)


        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        skus_page = paginator.page(page)

        # all pages < 5 ; current <= 3, 12345
        # current is the lastest 3
        # other <- <- cur -> ->
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]


        user = request.user
        cart_count = 0
        if user.is_authenticated():

            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)


        context = {'type':type, 'types':types,
                   'skus_page':skus_page,
                   'new_skus':new_skus,
                   'pages':pages,
                   'cart_count':cart_count,
                   'sort':sort}


        return render(request, 'list.html', context)
