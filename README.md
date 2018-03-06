# PicUploader

PicUploader could automatically upload images(from clipboard) and save Markdown links

## 功能描述

- 自动从ClipBoard获取图片并上传七牛云
- 从ClipBoard获取图片，并将其贴在屏幕上（待定，未开发）

## TODO

- [ * ] 设置界面加入`outside_catenary`.
- [ ] 将主界面除去，直接放入到系统托盘中
- [ ] 直接上传文件的功能
- [ ] 其他的图床上传方式
- [ ] 将图片贴在屏幕上（始终置顶）

## 需要的依赖：

- pyqt5
- qiniu

可使用`requirements.txt`文件来安装依赖：

```bash
pip install -r requirements.txt
```

**强烈建议使用`virtualenv`或类似工具安装依赖，因为PyQt5和PyQt4可能会有冲突。**

## Usage：

首先需要先创建`config.ini`文件，可参考`template_config.ini`，或者可以直接修改`template_config.ini`的名字为`config.ini`:

```config
[QINIU]
outside_catenary = ""
access_key = ""
secret_key = ""
bucket_name = ""
markdown = True
auto_copy = True
auto_upload = True
```

### 使用界面：

主界面：

![主界面](http://olrv1mriz.bkt.clouddn.com/18-03-06/003800)

- Copy按钮可以复制最近一次生成的Markdown外链
- Setting按钮进入设置

设置的界面

![设置界面](http://olrv1mriz.bkt.clouddn.com/18-03-06/004122)

首先是`Access Key`和`Secret Key`，可在七牛云个人中心的密钥管理中找到

然后是`Bucket Name`,即存储空间的名字

还有一个外链的域名（Outside Catenary)~~由于时间原因没有在GUI中显示，需要在`config.ini`中修改,**注意**，只给出域名即可，不要在前面和后面加入`http`或`/`等。~~

例如我的为：

```config
outside_catenary = olrv1mriz.bkt.clouddn.com
```

![](http://olrv1mriz.bkt.clouddn.com/18-03-06/005415)

最后是三个`checkbox`的含义分别为：

- auto loader: 是否自动的查看ClipBoard是否为图片，如果是，则上传
- auto_copy: 是否在上传完后将外链或Markdown格式的外链复制的ClipBoard，即剪贴版中
- markdown:即是否将外链转换为Markdown格式。

ps：所谓的Markdown格式即`![](url)`