配置文件读写逻辑需要提整，支持多个供应商。

1）供应商配置从指定文件或者从默认配置文件～/.qwen_coder_switch/provide.yml 读取。

2）yaml 格式如下：

```
provider:
  siliconflow:
    base_url: https://api.sophnet.com/v1
    balance_url: https://api.siliconflow.cn/v1/user/info
    balance_field: data.balance
    api_keys:
      - key1
      - key2
  sophnet:
    base_url: https://www.sophnet.com/api/open-apis/v1
    balance_url: https://api.sophnet.com/v1/balance
    balance_field: result.currentBalance
    api_keys:
      - key1
      - key2
```

字段说明：
base_url 是传给 qwen coder 的 baseUrl，balance_url 是获取用户额度的接口，
balance_field 是获取额度接口返回的额度字段，请求方式通常是
api_keys 是需要遍历的 apiKey

3）调用用户额度的接口方式如下：

```
curl --request GET \
  --url https://www.sophnet.com/api/open-apis/projects/balance \
  --header 'Authorization: Bearer $token
```
