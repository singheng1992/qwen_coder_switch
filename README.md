# qwen_coder_switch

实现 qwen-coder-cli 的密钥根据用户自定义的密钥池自动切换

## 安装

```
git clone https://github.com/singheng1992/qwen_coder_switch.git

cd qwen_coder_switch

pip install -e .
```

## 修改配置

配置文件路径：~/.qwen_coder_switch/provider.yml

## 用法

```
# 读取默认配置文件
qwen_coder_switch

# 或者指定配置文件路径
qwen_coder_switch -c /your_path/provider.yml
```

# 版本说明

## v0.1.0

针对硅基流动切换密钥

1）检查密钥额度是否充足，如果不足则删除无用的密钥
2）Qwen Code CLI 切换配置文件 apiKey 字段

## v0.2.0 provider.yml 格式调整

1）支持更多模型供应商

2）添加默认模型字段

## v0.3.0 切换策略调整

1）删去余额相关字段 balance_field、balance_url
2）支持多种切换模式： 顺序切换、倒序切换、随机切换，默认顺序切换。

顺序切换：从前往后，选择一个有效的 api_key 切换，
倒序切换：从后往前，选择一个有效的 api_key 切换，
随机切换：随机选择一个有效的 api_key 进行切换，

3）每次通过简单对话测试，
接口正常，则更新 qwen-coder-cli 的配置文件，然后退出程序；
接口异常，则删除 无效的 api_key，继续寻常下一个有效的 api_key。
