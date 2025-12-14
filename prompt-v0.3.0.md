1）删去余额相关字段 balance_field、balance_url

2）每次通过简单对话测试 api_key 是否有效
接口正常，则更新 qwen-coder-cli 的配置文件，然后退出程序；
接口异常，则删除 无效的 api_key，继续寻常下一个有效的 api_key。

{
"role": "user",
"message": "hi",
"max_token": 1
}

3）支持多种切换模式： 顺序切换、倒序切换、随机切换，默认顺序切换。

顺序切换：从前往后，选择一个有效的 api_key 切换，
倒序切换：从后往前，选择一个有效的 api_key 切换，
随机切换：随机选择一个有效的 api_key 进行切换，

4）增加配置文件回退命令

寻找指定目录或者默认目录下 provider*backup*\*.yml 文件，寻找日期最接近的进行覆盖

5）覆盖原来配置时请保持原来的供应商顺序
