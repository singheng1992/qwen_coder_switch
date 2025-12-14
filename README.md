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

## v0.1.0 针对硅基流动切换密钥

1）检查密钥额度是否充足，如果不足则删除无用的密钥
2）Qwen Code CLI 切换配置文件 apiKey 字段

## v0.2.0 provider.yml 格式调整，支持更多模型供应商
