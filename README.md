## EasySRC

这个项目旨在借助AI向代码文件添加详细注释，提升代码可读性，旨在让大型、复杂项目代码易于阅读。

你可以通过运行main.cpp来使用：![alt text](https://raw.githubusercontent.com/lgylgy1/EasySRC/main/image.png)

也可以通过二进制文件来使用：![alt text](https://raw.githubusercontent.com/lgylgy1/EasySRC/main/image-1.png)
直接在命令行运行二进制文件，并将需要注释的文件路径或者文件夹路径作为参数传入。

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
