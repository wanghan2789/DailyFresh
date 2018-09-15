# **DailyFresh**

* Background

  ​    DailyFresh属于经典的电商网站搭建项目，其主要是B2C面向生鲜类产品，应用于PC网页端的一个项目。本项目主要包含四个模块：**用户模块、商品模块、购物车模块、订单模块**。每一个模块的详细功能如下：

  * **用户模块**：`注册、登录、激活、退出`、个人中心、收货地址。
  * **商品模块**：首页、详情、列表、`搜索`。
  * **购物车**：`增、删、改、查`。
  * **订单模块**：确认订单页面、`创建订单、请求支付、(与支付宝的对接)、查询支付结果`、对订单的评论。


* 适用范围

  目前所采用的技术手段应该可以满足中小以及个人网站的使用，基本功能齐全，当然还有一些地方需要优化。

* 虚拟环境创建

  你可以创建一个虚拟环境来建立一个相对独立而且稳定的实验体系，当然，如果你需要真正部署这个项目，你可以在你的Linux服务器上直接进行部署(那么你可以跳过下面的部署)。

  `sudo pip install virtualenv`

  `sudo pip install virtualenvwrapper`

  修改你的环境变量(Note: 在虚拟环境下，不要用sudo安装，否则安装在主机上，你的mysql可以部署在主机上。)

  `export WORKON_HOME=$HOME/.virtualenvs`
  `export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3`
  `source /usr/local/bin/virtualenvwrapper.sh`

  `source ~/.bashrc`

  为与主机的mysql交互你需要安装pymysql

  `pip install pymysql`

* Redis的安装

  `tar -zxvf redis-3.2.8.tar.gz`

  `sudo mv ./redis-3.2.8 /usr/local/redis/`

  `cd /usr/local/redis/`

  `sudo make`

  `sudo make test #实际上可以省略，并且不是返回大量错误，都可以继续下一步`

  `sudo make install`

  `#配置redis`

  `sudo cp /usr/local/redis/redis.conf /etc/redis/`

  然后你可以按需求更改/etc/redis/redis.conf的内容。

* 配置安装FastDFS

  * 安装 libfastcommon

    下载libfastcommon-master.zip，解压并进入目录，执行 

    `./make.sh    #如果sh没有运行权限，你可以chmod +x`

    `sudo ./make.sh install`

  * 安装 FastDFS

    下载并解压fastdfs-master.zip，进入到 fastdfs-master目录中

    `make`

    `sudo make install`

  * 配置跟踪服务器tracker

    `sudo cp /etc/fdfs/tracker.conf.sample /etc/fdfs/tracker.conf`

    `本机名: malfoy`

    `在/home/malfoy/目录中创建目录 fastdfs/tracker`

    `mkdir –p /home/malfoy/fastdfs/tracker`

    `sudo vim /etc/fdfs/tracker.conf`

    `修改：`

    `base_path=/home/malfoy/fastdfs/tracker`

  * 配置存储服务器storage

    `sudo cp /etc/fdfs/storage.conf.sample /etc/fdfs/storage.conf`

    `#在/home/malfoy/fastdfs/ 目录中创建目录 storage`

    `mkdir –p /home/python/fastdfs/storage`

    `sudo vim /etc/fdfs/storage.conf`

    `#修改：`

    `base_path=/home/malfoy/fastdfs/storage`
    `store_path0=/home/malfoy/fastdfs/storage`
    `tracker_server=ip:port(for example: 127.0.0.1:22122)`

    `#启动服务器：`

    `sudo /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf start`

    `sudo /usr/bin/fdfs_storaged /etc/fdfs/storage.conf start`

  * 测试是tracker与storage是否安装成功:

    `sudo cp /etc/fdfs/client.conf.sample /etc/fdfs/client.conf`

    `sudo vim /etc/fdfs/client.conf`

    `#修改内容：`

    `base_path=/home/malfoy/fastdfs/tracker`
    `tracker_server=ip:22122`

    `#LoadFile:`

    `fdfs_upload_file /etc/fdfs/client.conf /home/malfoy/Desktop/T.txt`

    `#return:`

    `group1/M00/00/00/......txt`

    若成功返回上述，则代表目前为止配置是ojbk的。

  * 安装nginx及fastdfs-nginx-module

    这部分的安装较为繁琐，可能需要细心一些。

    ------

    首先安装两个依赖Debian

    `sudo apt-get install libpcre3 libpcre3-dev`
    `sudo apt-get install openssl libssl-dev`

    `#解压缩 nginx-1.8.1.tar.gz  解压缩 fastdfs-nginx-module-master.zip  进入nginx-1.8.1目录中`

    `sudo ./configure --prefix=/usr/local/nginx/ --add-module=fastdfs-nginx-module-master /home/malfoy/Desktop/nginx-1.8.1/src`

    `sudo make`

    `sudo make install`

    `#进入fastdfs-nginx-module-master/src`

    `sudo cp mod_fastdfs.conf /etc/fdfs/mod_fastdfs.conf`

    `sudo vim /etc/fdfs/mod_fastdfs.conf`

    `#修改为：`

    `connect_timeout=10`
    `tracker_server=ip:22122`
    `url_have_group_name=true`
    `store_path0=/home/malfoy/fastdfs/storage`

    `sudo cp http.conf /etc/fdfs/http.conf`

    `sudo cp mime.types /etc/fdfs/mime.types`

    `sudo vim /usr/local/nginx/conf/nginx.conf`

    `#修改：`

    ```shell
    server {
                listen       8888;
                server_name  localhost;
                location ~/group[0-9]/ {
                    ngx_fastdfs_module;
                }
                error_page   500 502 503 504  /50x.html;
                location = /50x.html {
                root   html;
                }
            }
    ```

    `#启动nginx：`

    `sudo /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf start`
    `sudo /usr/bin/fdfs_storaged /etc/fdfs/storage.conf start`
    `sudo /usr/local/nginx/sbin/nginx`

  * 使用python客户端上传测试

    `#下载：fdfs_client-py-master.zip`

    `#安装一些依赖的包：`

    `pip install mutagen`

    `pip install requests`

    `pip install fdfs_client-py-master.zip`

    `#然后进入交互界面：`

    >>> `from fdfs_client.client import Fdfs_client`
    >>> `client = Fdfs_client('/etc/fdfs/client.conf')`
    >>> `ret = client.upload_by_filename('test')`
    >>> `ret`
    >>> `{'Uploaded size': '0B', 'Status': 'Upload successed.', 'Group name': 'group1', 'Local file name': 'test', 'Remote file_id': 'group1/M00/00/00/wKjAgFuXHmSAK5rIAAAAAAAAAAA3374302', 'Storage IP': '192.168.192.128'}`

  * 除此之外，可能会漏掉一些库，因此进行了pip freeze，并将本机所有的lib以及其版本贴了出来。

    `amqp==2.3.2` `asn1crypto==0.24.0` `billiard==3.5.0.4` `celery==4.2.1`
    `certifi==2018.8.24` `cffi==1.11.5` `chardet==3.0.4` `cryptography==2.3.1`
    `Django==1.8.2` `django-haystack==2.6.0` `django-redis==4.0.0``django-redis-sessions==0.5.6` `django-tinymce==2.6.0` `fdfs-client-py==1.2.6` `idna==2.7`
    `itsdangerous==0.24` `jieba==0.39` `kombu==4.2.1` `mutagen==1.41.1`
    `Pillow==3.4.1` `pycparser==2.18` `pycryptodomex==3.6.6` `PyMySQL==0.9.2`
    `python-alipay-sdk==1.8.0` `pytz==2018.5` `redis==2.10.6` `redis-py-cluster==1.3.5` `requests==2.19.1` `six==1.11.0` `urllib3==1.23`
    `uWSGI==2.0.17.1` `vine==1.1.4` `Whoosh==2.7.4`

* 用户中心：Django默认的认证系统: AbstractUser

  * 创建用户模型类的时候，直接进行继承。
  * 你创建的admin也会在user里面。
  * login_required装饰器，可以对用户登录行为的判断。
  * 用户注册：
    * 在核心注册之前，已经进行了数据校验。
    * 对需要激活的用户，为了保证我们地址，服务器规律的安全，我们队激活地址（包含用户信息），利用itsdangerous对信息进行加密，生成token，同时可以设置链接的有效时间。
    * 激活邮件发送：可以利用Django进行发送。但是邮件发送过程中，进程阻塞，用户体验较差。于是借助celery进行异步发送。通过代码发送任务，利用redis作为中间人，最后选择一个服务器作为处理，专门处理任务(必须有外网，也必须有任务代码)。
  * 用户登录：利用redis作为缓存。不但判断了用户名密码是否匹配，还对激活进行了校验
    * 有些页面应该为用户登陆之后才能进行访问：装饰器，闭包函数。如果你没有登录，会跳转到登录页面。也可以写一个继承与MixIn的类。
  * logout函数清除用户的session信息。
  * redis存储历史浏览记录
    * 用户访问商品后，会添加一条历史浏览记录。
    * 当用户访问个人信息页面的时候获取历史浏览记录。
    * 历史浏览记录存于redis中，redis作为内存型数据库，存取速度远远高于mysql
    * 我们选择每个用户的历史浏览记录用一条数据保存，list，新的浏览产生时，进行一个头插。

* 商品模块：

  * 使用FastDFS的好处：
    * 海量存储，扩容方便。
    * 解决文件内容重复问题。(hash指纹)
    * 结合nginx提高网站访问图片的效率。
  * 商品首页
    * 首页更换较少，因此进行静态优化。也就是将原本动态处理的页面渲染结果保存为html。提高性能。
    * 管理员修改信息，则通过celery对首页的静态页面重新渲染静态页面。
    * 通过admin后台管理，当Goods的增删出现，附加删除缓存的动作。当没有缓存，则需要去数据库查询，并缓存。
    * 这样做的好处：能一定程度防止DDOS恶意攻击，减少数据库查询次数。
  * 商品搜索-搜索引擎
    * 搜索引擎： 可以对表中的某些关键词进行分析，简历索引数据。
    * 全文搜索框架：帮助用户使用搜索引擎。
    * 我们采用haystack + whoosh +jieba 对字段进行搜索，能够较好地支持中英文搜索。

* 购物车模块

  * 我们对前端传递的数据进行了校验。
  * 采用post的方式接收数据。
  * 利用ajax提升用户体验。

* 订单模块

  * 订单生成：
    * 用户下单后，会向order表中增加记录。
    * 用户订单中有几个商品，会向goods中增加几条记录。
    * 借助mysql事务，对高并发秒杀类行为进行优化。你可以选择在冲突较少的时候使用乐观锁，也可以在冲突较多的时候使用悲观锁。
  * 订单支付(对接支付宝)：

* 部署：

  你可以借助nginx和uwsgi进行项目部署，实现负载均衡。

  ​

