from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db import transaction
from django.views.generic import View
from django.conf import settings


from apps.user.models import Address
from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo, OrderGoods

from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from datetime import datetime
from alipay import AliPay
import os

# Create your views here.

class OrderPlaceView(LoginRequiredMixin, View):

    def post(self, request):

        user = request.user
        sku_ids = request.POST.getlist('sku_ids') # [1,26]


        if not sku_ids:
            return redirect(reverse('cart:show'))

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        skus = []
        total_count = 0
        total_price = 0

        for sku_id in sku_ids:

            sku = GoodsSKU.objects.get(id=sku_id)

            count = conn.hget(cart_key, sku_id)

            amount = sku.price*int(count)

            sku.count = count

            sku.amount = amount

            skus.append(sku)

            total_count += int(count)
            total_price += amount


        transit_price = 10 # must


        total_pay = total_price + transit_price


        addrs = Address.objects.filter(user=user)


        sku_ids = ','.join(sku_ids) # [1,25]->1,25
        context = {'skus':skus,
                   'total_count':total_count,
                   'total_price':total_price,
                   'transit_price':transit_price,
                   'total_pay':total_pay,
                   'addrs':addrs,
                   'sku_ids':sku_ids}

        return render(request, 'place_order.html', context)



class OrderCommitView(View):
    # this decoration could build a SW
    @transaction.atomic
    def post(self, request):

        user = request.user
        if not user.is_authenticated():

            return JsonResponse({'res':0, 'errmsg':'login'})

        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids') # 1,3


        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res':1, 'errmsg':'cata not complete'})


        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res':2, 'errmsg':'what do you want to pay?'})


        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:

            return JsonResponse({'res':3, 'errmsg':'addr illegal'})

        # todo core deal


        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)


        transit_price = 10
        total_count = 0
        total_price = 0


        #save points
        save_id = transaction.savepoint()
        try:


            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)


            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id

            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                for i in range(3):

                    try:
                        #select_for_update(). pessmistic lock
                        # sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except:
                        transaction.savepoint_rollback(save_id)

                        return JsonResponse({'res':4, 'errmsg':'NULL Goods'})


                    count = conn.hget(cart_key, sku_id)

                    #store force
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 6, 'errmsg': 'No Enough Goods'})

                    # sku.stock -= int(count)
                    # sku.sales += int(count)
                    # sku.save()

                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count)
                    new_sales = sku.sales + int(count)

                    res = GoodsSKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 7, 'errmsg': 'failuer without source'})
                        continue



                    OrderGoods.objects.create(order=order,
                                              sku=sku,
                                              count=count,
                                              price=sku.price)




                    amount = sku.price*int(count)
                    total_count += int(count)
                    total_price += amount
                    break


            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res':7, 'message':'Some thing wrong'})



        transaction.savepoint_commit(save_id)
        conn.hdel(cart_key, *sku_ids)

        return JsonResponse({'res':5, 'message':'Ok'})


class OrderPayView(View):
    def post(self, request):

        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res':0, 'errmsg':'login'})

        order_id = request.POST.get('order_id')

        if not order_id:
            return JsonResponse({'res':1, 'errmsg':'NULL id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res':2, 'errmsg':'Error'})


        alipay = AliPay(
            appid="2016092100563402", # app id
            app_notify_url=None,  # callback url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'), # alipay public key
            sign_type="RSA2",  # RSA or RSA2
            debug=True  # default = False
        )

        # Alipay surface
        # goto https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.total_price+order.transit_price # Decimal
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id, # id
            total_amount=str(total_pay), # all for jason , you should use str
            subject='Daily Fresh%s'%order_id,
            return_url=None,
            notify_url=None  # default = notify url
        )

        # return request
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res':3, 'pay_url':pay_url})



class CheckPayView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': 'login'})


        order_id = request.POST.get('order_id')


        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': 'NULL id'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': 'ERROR'})


        alipay = AliPay(
            appid="2016092100563402",
            app_notify_url=None,
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=True
        )

        while True:
            response = alipay.api_alipay_trade_query(order_id)

            # response = {
            #         "trade_no": "2017032121001004070200176844", # 支付宝交易号
            #         "code": "10000", # 接口调用是否成功
            #         "invoice_amount": "20.00",
            #         "open_id": "20880072506750308812798160715407",
            #         "fund_bill_list": [
            #             {
            #                 "amount": "20.00",
            #                 "fund_channel": "ALIPAYACCOUNT"
            #             }
            #         ],
            #         "buyer_logon_id": "csq***@sandbox.com",
            #         "send_pay_date": "2017-03-21 13:29:17",
            #         "receipt_amount": "20.00",
            #         "out_trade_no": "out_trade_no15",
            #         "buyer_pay_amount": "20.00",
            #         "buyer_user_id": "2088102169481075",
            #         "msg": "Success",
            #         "point_amount": "0.00",
            #         "trade_status": "TRADE_SUCCESS", # 支付结果
            #         "total_amount": "20.00"
            # }

            code = response.get('code')

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':

                trade_no = response.get('trade_no')

                order.trade_no = trade_no
                order.order_status = 4
                order.save()

                return JsonResponse({'res':3, 'message':'Succeed'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):

                import time
                time.sleep(5)
                continue
            else:

                print(code)
                return JsonResponse({'res':4, 'errmsg':'Failure'})


class CommentView(LoginRequiredMixin, View):

    def get(self, request, order_id):

        user = request.user


        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))


        order.status_name = OrderInfo.ORDER_STATUS[order.order_status]


        order_skus = OrderGoods.objects.filter(order_id=order_id)
        for order_sku in order_skus:

            amount = order_sku.count*order_sku.price

            order_sku.amount = amount

        order.order_skus = order_skus


        return render(request, "order_comment.html", {"order": order})

    def post(self, request, order_id):

        user = request.user

        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))


        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        for i in range(1, total_count + 1):

            sku_id = request.POST.get("sku_%d" % i) # sku_1 sku_2

            content = request.POST.get('content_%d' % i, '') # cotent_1 content_2 content_3
            try:
                order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue

            order_goods.comment = content
            order_goods.save()

        order.order_status = 5 # finish
        order.save()

        return redirect(reverse("user:order", kwargs={"page": 1}))

