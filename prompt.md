需要 python 开发一个命令行工具，基于 typer、rich 框架，
版本要求
typer==0.20.0
rich==14.2.0

每次执行本工具，实现以下功能：
1）检查密钥配置 yaml 文件是否存在

密钥文件可以在命令行指定，
也可以放在默认目录下：～/.qwen_coder_switch/provide.yml；
如果密钥配置不存在，生成一个默认的密钥配置文件；
如果指定的文件不存在，提示错误

2） 检查密钥配置格式是否正确：

一级目录是 provider，
二级目录是各个供应商的名称，
二级目录的值是各个供应商的 apiKey 列表

```yaml
provider:
  siliconflow:
    - sk-xxx
    - sk-xxx
  dmxapi:
    - sk-xxx
    - sk-xxx
```

3）检查所有密钥额度是否充足
检查以下接口 balance 的值是否大于 0；
如果小于等于 0，则删除该密钥，
如果接口异常，则删除该密钥，并命令行提示错误。
删除密钥前请备份一下历史文件，以时间格式命名。

curl --request GET \
 --url https://api.siliconflow.cn/v1/user/info \
 --header 'Authorization: Bearer sk-xxxx'

{"code":20000,"message":"Ok","status":true,"data":{"id":"d4q60sucnncc73e68fd0","name":"个人","image":"","email":"","isAdmin":false,"balance":"13.8925","status":"normal","introduction":"","role":"","chargeBalance":"0","totalBalance":"13.8925","category":"0"}}

4）切换配置文件 apiKey 字段
配置文件默认路径在在~/.qwen/settings.json，
选择其中一个有效的 apikey 进行替换
数据格式如下：

```json
{
  "$version": 2,
  "security": {
    "auth": {
      "selectedType": "openai",
      "apiKey": "sk-xxx",
      "baseUrl": "https://api.siliconflow.cn/"
    }
  },
  "model": {
    "name": "zai-org/GLM-4.6"
  }
}
```
