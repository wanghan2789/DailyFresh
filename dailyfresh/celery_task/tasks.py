from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

from django.template import loader, RequestContext

# in your task add
import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

from apps.goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection


app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')


@app.task
def send_register_active_email(to_email, username, token):
    subject = '欢迎注册我们的账号'
    # context = '<h1>%s, welcom go here, you are would be the vip by next step,click here </br> <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a> </h1>'%(username, token, token)
    # context = '<h1>%s, welcom go here, you are would be kill all MAN next step,click here </br> <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a> </h1>'%(username, token, token)
    # context = '''<table width="100%" border="1" bordercolor="#000000"><tr bordercolor="#FFFFFF"><td>%s, welcome go here, you are would be the vip by next step, click </br><a href="http://192.168.192.128:8000/user/active/%s">here</a>.</br>Also, you can copy this address to complete register : http://192.168.192.128:8000/user/active/%s </td></tr></table><p>'''%(username, token, token)
    # context = '<table width = "100%" border="1" bordercolor="#000000"><tr bordercolor="#FFFFFF"><td>Dear %s, welcome go here, you would become our vip by next step, please click <a href="http://192.168.192.128:8000/user/active/%s">here</a>.</br>Also, you can copy this address to your browers to complete registe : http://192.168.192.128:8000/user/active/%s </td></tr></table>'%(username, token, token)
    # context = '<td>Dear %s, welcome go here, you would become our vip by next step, please click <a href="http://192.168.192.128:8000/user/active/%s">here</a>.</br>Also, you can copy this address to your browers to complete registe : http://192.168.192.128:8000/user/active/%s </td></tr></table>'%(username, token, token)
    # context = " <table width = '100%' border='1' bordercolor='#000000'> <tr bordercolor='#FFFFFF'> "

    context = 'Dear %s, welcome go here, you would be our vip by next step, please click  <a href="http://192.168.192.128:8000/user/active/%s">here</a>. </br>Also, you can copy this address to your browers to complete regist : http://192.168.192.128:8000/user/active/%s' % (username, token, token)
    massage = context
    sender = settings.EMAIL_FROM
    reciever = [to_email]
    send_mail(subject, context,sender, reciever,html_message=massage)

    # pass


@app.task
def generate_static_index_html():

    types = GoodsType.objects.all()


    goods_banners = IndexGoodsBanner.objects.all().order_by('index')


    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')


    for type in types:  # GoodsType

        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')

        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')


        type.image_banners = image_banners
        type.title_banners = title_banners



    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}


    temp = loader.get_template('static_index.html')

    static_index_html = temp.render(context)


    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)


