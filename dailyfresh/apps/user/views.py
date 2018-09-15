from django.shortcuts import render,redirect
from apps.user.models import User,Address
from django.core.urlresolvers import reverse
from django.views.generic import View
import re
from django.core.paginator import Paginator
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.http import HttpResponse
from apps.order.models import OrderInfo,OrderGoods
from django.core.mail import send_mail
from celery_task.tasks import send_register_active_email
from django.contrib.auth import authenticate,login,logout
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU
# Create your views here.
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, email]):
            return render(request, 'register.html', {"errmsg": "data not complete"})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {"errmsg": "email not legal"})
        if allow != 'on':
            return render(request, 'register.html', {"errmsg": "you did not agree our contract"})
        # user = User()
        # user.username = username
        # user.password = password
        # user.save()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': 'the name is exit'})
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        return redirect(reverse('goods:index'))

def register_handle(request):
    # pass
    #data crc deal return
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')

    if not all([username, password, email]):
        return render(request, 'register.html', {"errmsg":"data not complete"})
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {"errmsg": "email not legal"})
    if allow != 'on':
        return render(request, 'register.html', {"errmsg": "you did not agree our contract"})
    # user = User()
    # user.username = username
    # user.password = password
    # user.save()
    try:
        User.objects.get(username = username)
    except User.DoesNotExist:
        user = None
    if user:
        return render(request, 'register.html', {'errmasg':'the name is exit'})
    user = User.objects.create_user(username,email,password)
    user.is_active = 0
    user.save()
    return redirect(reverse('goods:index'))

class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')
    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, email]):
            return render(request, 'register.html', {"errmsg": "data not complete"})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {"errmsg": "email not legal"})
        if allow != 'on':
            return render(request, 'register.html', {"errmsg": "you did not agree our contract"})
        # user = User()
        # user.username = username
        # user.password = password
        # user.save()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'register.html', {'errmasg': 'the name is exit'})
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        #send a email
        #encode user id create token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()



        # subject = '欢迎注册我们的账号'
        # context = '<h1>%s, welcom go here, you are would be the vip by next step,click here </br> <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a> </h1>'%(username, token, token)
        # # context = '<h1>%s, welcom go here, you are would be kill all MAN next step,click here </br> <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a> </h1>'%(username, token, token)
        # massage = context
        # sender = settings.EMAIL_FROM
        # reciever = [email]
        # send_mail(subject, context,sender, reciever,html_message=massage)
        send_register_active_email.delay(email, username, token)





        return redirect(reverse('goods:index'))

class ActiveView(View):
    def get(self,request,token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            return HttpResponse('the link is time out!')



class LoginView(View):
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''


        return render(request, 'login.html',{'username':username,'checked':checked})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'data not complete'})
        user = authenticate(username= username,password=password)
        if user is not None:
            if user.is_active:
                #state session
                login(request, user)

                next_url = request.GET.get('next',reverse('goods:index'))
                # if next_url is None:


                response = redirect(next_url)

                remember = request.POST.get('remember')
                if (remember == 'on'):
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response





            else:
                return render(request, 'login.html', {'errmsg':'active is not complete'})
        else:
            return render(request, 'login.html', {'errmsg':'username/password is wrong!'})




        return render()

class LogoutView(View):
    def get(self,requset):
        logout(requset)
        return redirect(reverse('goods:index'))



class UserInfoView(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        address = Address.objects.get_default_address(user)

        #from redis import StrictRedis
        #sr = StrictRedis(host='localhost',port=6379,db=9)
        con = get_redis_connection('default')
        history_key = 'history_%d'%user.id
        sku_ids = con.lrange(history_key, 0, 4)  # [2,3,1]

        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # all image
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li}

        return render(request, 'user_center_info.html', context)
        # return render(request, 'user_center_info.html', {'page':'user','address':address})

class UserOrderView(LoginRequiredMixin, View):
    def get(self,request, page):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')


        for order in orders:

            order_skus = OrderGoods.objects.filter(order_id=order.order_id)


            for order_sku in order_skus:

                amount = order_sku.count * order_sku.price

                order_sku.amount = amount

            print(order.order_status)
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # print(order.order_status)
            # print(order.status_name)

            order.order_skus = order_skus


        paginator = Paginator(orders, 1)


        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1


        order_page = paginator.page(page)


        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)


        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}


        return render(request, 'user_center_order.html', context)


        # return render(request, 'user_center_order.html', {'page':'order'})

class AddressView(LoginRequiredMixin, View):
    def get(self,request):
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True) # models.Manager
        # except Address.DoesNotExist:

        address = Address.objects.get_default_address(user)

        # address = None
        return render(request, 'user_center_site.html',{'page':'address', 'address':address})

    def post(self,request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'data not complete'})
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        return redirect(reverse('user:address'))
















