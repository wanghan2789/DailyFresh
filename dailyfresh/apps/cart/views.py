from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
# Create your views here.

#add goods in your cart
class CartAddView(View):
    def post(self, request):
        #receive proof deal return
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': 'please login'})



        if not all([sku_id,count]):
            return JsonResponse({'res':1, 'errmsg':'data not complete'})


        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': 'num wrong'})


        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': 'not exit'})
        #pass

        #deal
        conn = get_redis_connection('default')
        #if exit then do add
        cart_key = 'cart_%d' % user.id
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            count += int(cart_count)

        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': 'not enough'})


        conn.hset(cart_key, sku_id, count)
        total_count = conn.hlen(cart_key)

        return JsonResponse({'res': 5, 'total_count': total_count, 'message': 'ok'})

#there is no ajax deal, the acquire could be
#presented in the front, so we can use Login method
class CartInfoView(LoginRequiredMixin, View):


    def get(self, request):
        user = request.user
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id

        cart_dict = conn.hgetall(cart_key)

        skus = []

        total_count = 0
        total_price = 0

        for sku_id, count in cart_dict.items():

            sku = GoodsSKU.objects.get(id=sku_id)

            amount = sku.price * int(count)

            sku.amount = amount

            sku.count = count

            skus.append(sku)


            total_count += int(count)
            total_price += amount


        context = {'total_count': total_count,
                   'total_price': total_price,
                   'skus': skus}


        return render(request, 'cart.html', context)


class CartUpdateView(View):

    def post(self, request):

        user = request.user
        if not user.is_authenticated():

            return JsonResponse({'res': 0, 'errmsg': '请先登录'})


        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')


        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': 'data not complete'})


        try:
            count = int(count)
        except Exception as e:

            return JsonResponse({'res': 2, 'errmsg': 'num wrong'})


        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:

            return JsonResponse({'res': 3, 'errmsg': 'goods not exits'})


        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id


        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'goods sell out '})


        conn.hset(cart_key, sku_id, count)


        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)


        return JsonResponse({'res':5, 'total_count':total_count, 'message':'succeed'})


# del ajax
class CartDeleteView(View):

    def post(self, request):

        user = request.user
        if not user.is_authenticated():

            return JsonResponse({'res': 0, 'errmsg': 'log first'})


        sku_id = request.POST.get('sku_id')


        if not sku_id:
            return JsonResponse({'res':1, 'errmsg':'a not real id'})


        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:

            return JsonResponse({'res':2, 'errmsg':'not exit'})


        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        # del
        conn.hdel(cart_key, sku_id)


        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)


        return JsonResponse({'res':3, 'total_count':total_count, 'message':'del succeed'})








