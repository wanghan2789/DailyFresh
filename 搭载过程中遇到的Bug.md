* ##### 基础格式：发生时间，Bug描述，解决方案。

* 2018/09/09日14:35:29 $

  描述：  pycharm把.py文件识别成.text文件，代码提示没有了，改掉文件名才能出现提示。 可能是因为创造文件的时候不小心把这个文件名与text关联了。

  解决方案：  File->Settings->Editor->File Types 里面找到text，然后在text里找到这个文件名，删除就可以了

* 2018年9月9日14:55:55 $

  描述：  setting的user写成了usr导致**404**, 修改完成后，出现无法找到register的错误，原因是对应user模块的url，写到了cart中。

  解决方案：  按照合理的修改方式修改。

* 2018年9月9日16:25:46 $

  描述：  Django出现**Conflicting**的奇怪报错，原因是从不同的路径导入相同的。

  解决方案：  请写全路径 原本 from user.models import User已改为 from apps.user.models import User

* 2018年9月9日17:29:26 $

  描述：  Basemodel 参数错误，导致模型中存在NULL的数据。

  解决方案：  models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

* 2018年9月10日09:18:52 $

  描述：  redis serve无法启动。

  解决方案：  如果没有自定义环境变量，你可以--> sudo redis-server /etc/redis/redis.conf  说明：如果进行了conf的配置，就应当加载配置文件 。

* 2018年9月10日09:38:14 $

  描述：  部署的异步celery 无法发送邮件，原因为无法初始化。

  解决方案：

  `#Add this in your task`

  ` import os`
  `import django`
  `from django.core.wsgi import get_wsgi_application`

  `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")`
  `django.setup()`

* 2018年9月10日22:51:42 $

  描述：由于不得不重启服务器，需要重启需要的服务，特记录需要手动开启的服务。

  解决方案：

  `celery -A celery_task.tasks worker -l info`
  `sudo redis-server /etc/redis/redis.conf`
  `不要忘记开启redis和celery`
  `sudo /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf start`
  `sudo /usr/bin/fdfs_storaged /etc/fdfs/storage.conf start`
  `sudo /usr/local/nginx/sbin/nginx`

* 2018年9月11日09:58:43 $

  描述：无法找到celery pack。

  解决方案：认进入环境以及项目目录。 workon yourenvironmentname

* 2018年9月12日21:39:38 $

  描述： 报错信息

  `error massage: django.core.exceptions.ImproperlyConfigured: Requested setting CACHES, but settings are not configured. You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.`

  解决与分析：  在修改优化静态首页的时候，celery的tasks.py在修改过程中忘记了djanfo.setup()，导致未导入django，导致报错。也就是说，未注册Django的时候不能导入相应永久物。

* 2018年9月12日22:06:36 $

  描述：  nginx配置报错：

  `nginx: [emerg] "server" directive is not allowed here in /usr/local/nginx//conf/nginx.conf:46`

  解决方案：  注意检查{}配对情况，注意检查是否写出去了。

* 2018年9月13日09:35:07 $

  描述：

  The current URL, index, didn't match any of these.

  修改正则后确认没有笔误，这类匹配出错的原因一般都是因为正则书写错误。

* 2018年9月13日13:53:59 $

  描述：  报错

  `NoReverseMatch at /`
  `Reverse for 'show' with arguments '()' and keyword arguments '{}' not found. 1 pattern(s) tried: ['(\\d+)$']`

  分析与解决：  提示为反向解析过程找不到正则匹配的参数。这是由于**数据库未导入数据**，自定义数据集即可解决该问题。(也要考虑是不是相关模板写错了)
  url(r'^goods/(?P<goods_id>\d+)$', DetailView.as_view(), name='detail'),
  <li><a href="{% url 'goods:detail' banner.sku.id %}"><img src="{{ banner.image.url }}" alt="幻灯片"></a></li>

  ​

* 2018年9月13日20:53:46 $.

  描述：  search只能进行最精确的搜索，不能进行模糊搜索，例如我导入了apple数据，但是我只能搜索apple，不能搜索ap

  解决方案：  使用jieba分词。

* 2018年9月15日12:14:39 $

  描述：  Exception Type: 	KeyError

  解决方案：  在定义order model 的状态字典的时候，忘记修改顺序。字典方式写成{“unpaid” : 1}，调用的时候调用的key = 1，导致报错。


