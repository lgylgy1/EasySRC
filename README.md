## EasySRC

这个项目旨在借助AI向代码文件添加详细注释，提升代码可读性，旨在让大型、复杂项目代码易于阅读。

你可以通过运行main.py来使用。

注意：无论是二进制文件还是运行代码，请确保可执行文件运行路径下存在config.json配置文件。配置文件参考如下：
```json
{
  "api_key": "这里写你的API_KEY",
  "api_url": "这里写你的API_URL",
  "model": "这里写你api调用的模型名称",
  "max_tokens": "这里写你api调用的最大token数量",
  "text_extensions": [".txt",".json",".hpp","这个列表里面是需要处理的文件后缀"]
}
```
