# Vlab OAuth2 Example

一个 Flask 示例应用，演示如何不使用 OAuth2 第三库的情况下接入。

## 样例

<https://vlab-oauth-example.taoky.moe>

## 登录流程

代码：[app/main.py](app/main.py)

1. 提供预期的 callback URL，并申请得到 client ID、client secret。其中 client ID 可以暴露，client secret 不可以。
2. 用户浏览器访问 `https://vlab.ustc.edu.cn/o/authorize/?response_type=code&client_id={CLIENT_ID}&redirect_url={REDIRECT_URL}&state={state}`
    - REDIRECT_URL 即提供的 callback URL
    - state 为服务端随机生成的字符串（每次访问都需要不一样，因此这个字符串需要保存在 session 中）
    - 接口也支持 PKCE（`code_challenge` 参数，本样例不涉及）
3. 用户同意访问后（Vlab 相关应用可以设置不显示同意框），Vlab 会让浏览器跳转回 callback，URL query 中包含 `code` 和 `state`。
4. 服务端对比 `state` 和之前随机生成的一致后，服务端向 `https://vlab.ustc.edu.cn/o/token/` POST data 如下：
    - `client_id`
    - `client_secret`
    - code：callback 得到的 code
    - `grant_type`: 字符串 `"authorization_code"`
5. `/o/token/` 会返回一个 JSON，其中至少包含 `access_token`, `refresh_token`。`access_token` 有效期一小时。
    - 由于目前只提供访问用户信息的功能，因此可以获取 token 之后立刻获取用户信息。
6. 服务端 GET `https://vlab.ustc.edu.cn/vm/oapi/userinfo`，`Authorization` 头为 `Bearer` + 空格 + 你得到的 access token。返回的 JSON 中，`gid` 为用户的 GID（对于校内用户，与一卡通上的 GID 一致，**保持不变**），`username` 为用户名（对于校内用户，与最新的学号/工号一致，**可能会变化**）。
