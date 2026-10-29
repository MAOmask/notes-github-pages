# 3x-ui 面板伪装隐藏方案（迁移存档 v2）

> 归档时间：2026-10-29（v2 修订：补齐前置条件、防火墙风险、CF 真实 IP、回滚与验收标准）
> 来源机器：当前土耳其 VPS（域名 `es.000486000.xyz`，Cloudflare 代理 → 源站 8443）
> 用途：换美国 VPS 后，让新机器上的 AI 按本文件一次性复刻这套伪装

---

## 一、这套方案达成什么效果

| 访问者看到的 | 实际指向 |
|---|---|
| `https://es.000486000.xyz/` | LightNVR 监控后台（伪装站，看起来就是个 NVR 录像系统） |
| `https://es.000486000.xyz/kjJLZrSlkDxHsHwl4RoD7I/` | 3x-ui 面板（先过 nginx basic auth，再输面板账号密码） |
| 其他任意路径 | 回到伪装站 / 404 |

关键点：**监控站本身是真实可用的服务**，不是静态假页面，所以指纹上更自然。3x-ui 面板不占用任何独立端口对外暴露，只监听 `127.0.0.1`。

---

## 二、现有真实参数（实测，非推测）

### 2.1 nginx 反代层
- 文件：`/etc/nginx/sites-enabled/camouflage`（已备份为 `nginx/camouflage.conf`）
- 监听：`0.0.0.0:8443 ssl http2`，`server_name es.000486000.xyz`
- 证书：Cloudflare Origin CA
  - `/etc/ssl/certs/es.000486000.xyz.pem`
  - `/etc/ssl/private/es.000486000.xyz.key`
- 隐藏入口：`location /kjJLZrSlkDxHsHwl4RoD7I/`
  - `auth_basic` 开启，密码文件 `/etc/nginx/.htpasswd_xui`（备份为 `nginx/.htpasswd_xui`，用户名 `gdZzv5Ua`）
  - `proxy_pass https://127.0.0.1:9266`（`proxy_ssl_verify off`，因自签/Origin 证书链）
  - WebSocket 升级头、`proxy_read_timeout 3600s`（面板长连接必需）
- 根路径：`location /` → `proxy_pass http://127.0.0.1:20552`（LightNVR）

### 2.2 3x-ui 面板层
- 二进制：`/bin/x-ui`，配置库：`/etc/x-ui/x-ui.db`
- `webPort` = `9266`
- `webBasePath` = `/kjJLZrSlkDxHsHwl4RoD7I/`（与 nginx location **完全一致**，这一条是隐藏的核心）
- `webCertFile` / `webKeyFile` 复用同一张 Origin CA 证书
- 只监听本机，公网无法直连 9266

### 2.3 LightNVR 伪装站（Docker）
- compose：`/opt/lightnvr/docker-compose.yml`（已备份为 `lightnvr/docker-compose.yml`）
- 容器名 `lightnvr`，镜像 `ghcr.io/opensensor/lightnvr:latest`
- 端口：`127.0.0.1:20552 -> 8080/tcp`（只绑本机）
- 挂载：`./config:/etc/lightnvr`、`./data:/var/lib/lightnvr/data`
- `restart: unless-stopped`，`mem_limit: 512m`，`TZ=Asia/Shanghai`
- 后台初始账号 `admin / admin`（见 `lightnvr/lightnvr.ini`，**部署后务必改掉**）

### 2.4 三层防线
1. Cloudflare WAF / IP 白名单（面板路径仅自己的 IP 可访问）
2. nginx basic auth（第二道密码）
3. 3x-ui 面板自身账号密码（第三道密码）

---

## 三、目录内容

```
3x-ui-camouflage-kit/
├── README.md                        ← 本文件（含迁移提示词，可直接整段复制给新机器 AI）
├── cert/
│   ├── es.000486000.xyz.pem         ← Cloudflare Origin CA 证书（域名不变可直接复用）
│   └── es.000486000.xyz.key         ← 对应私钥（权限 600，敏感）
├── nginx/
│   ├── camouflage.conf              ← 原 nginx 站点配置（含 IP/域名/路径，需按新环境改）
│   └── .htpasswd_xui                ← basic auth 密码文件（含哈希，勿外泄）
├── lightnvr/
│   ├── docker-compose.yml           ← 伪装站编排（可直接复用）
│   ├── lightnvr.ini                 ← 伪装站主配置（含 admin/admin 初始口令）
│   └── go2rtc/go2rtc.yaml           ← 摄像头流配置，搬迁时可原样还原
└── x-ui/
    └── x-ui-settings.txt            ← 面板侧需要手工对齐的参数清单
```

> 敏感文件：`cert/*.key`、`nginx/.htpasswd_xui`、`lightnvr/lightnvr.ini`。建议整个目录 `chmod 700`，不要放进任何仓库或云同步盘。

---

## 四、迁移到美国 VPS 时要改什么

| 项目 | 是否要改 | 说明 |
|---|---|---|
| LightNVR compose | 不用改 | 全是相对路径 + 127.0.0.1 绑定，直接搬 |
| nginx `camouflage.conf` | 改少量 | `server_name` 换成新域名（若沿用旧域名则不改）；证书路径换成新签的；隐藏路径建议**重新随机生成** |
| Cloudflare Origin CA 证书 | 可复用 | 证书绑定域名不绑 IP，域名不变就能直接用 |
| 3x-ui `webPort` / `webBasePath` | 手动设 | 由主人自己装好后在面板「面板设置」里填，必须和 nginx location 完全一致 |
| 防火墙 | 要改 | 只放行 22/80/443/8443（或只放行 CF 回源 IP），**千万别照搬旧机器的 ufw 规则**，小心把自己 SSH 锁在外面 |
| Cloudflare DNS | 要改 | A 记录指向新 IP，橙云保持开启 |

---

## 五、给新机器 AI 的施工提示词（整段复制，`<尖括号>` 全部替换成实际值）

```text
你正在为一台全新的美国 VPS 上部署「3x-ui 面板伪装隐藏」方案。请严格按以下规格执行，
不要自创目录结构、不要省略步骤、不要用「大概/应该」代替验证。

==================== 目标效果 ====================
访问 https://<域名>/            → 看到真实运行的 LightNVR 监控后台（伪装站）
访问 https://<域名>/<隐藏路径>/ → 先弹 HTTP Basic 认证，通过后才是 3x-ui 登录页
其他任意路径                    → 不得暴露面板内容
3x-ui 面板不得监听任何公网端口，只允许 127.0.0.1。

==================== 开工前必做 ====================
1. 报告环境现状：发行版与版本、是否 root、nginx 版本、docker/compose 版本、
   ufw/iptables 现状、8443 与 20552 是否已被占用（ss -tlnp）。
2. 若 docker 或 nginx 未安装，先告诉我你打算怎么装（apt 还是官方脚本），等我同意。
3. 输出一份完整执行计划（含每步要改的文件、要新建的目录、要改的端口），
   等我确认后再动手。任何一步失败，先报告原因和备选方案，不要自行绕过。

==================== 需要我提供的信息 ====================
1. 域名（例：es.example.com）
2. Cloudflare Origin CA 证书 crt 与 key 的文件路径（或内容）
3. 3x-ui 的 webPort、登录账号（webBasePath 由你和我一起定）
4. 隐藏路径：若我没给，就生成 20 位以上随机大小写字母数字串并告诉我
5. basic auth 用户名与密码（或让我自己输入，你不要写进日志和聊天记录）

==================== 第一步：部署伪装站 LightNVR ====================
- 建目录 /opt/lightnvr，含 config/、data/、config/go2rtc/ 三个子目录
- 写 /opt/lightnvr/docker-compose.yml：
  services:
    lightnvr:
      image: ghcr.io/opensensor/lightnvr:latest
      container_name: lightnvr
      restart: unless-stopped
      mem_limit: 512m
      ports:
        - "127.0.0.1:20552:8080"
      volumes:
        - ./config:/etc/lightnvr:rw
        - ./data:/var/lib/lightnvr/data:rw
      environment:
        - TZ=Asia/Shanghai
- 注意：端口必须写成 127.0.0.1:20552:8080，禁止写成 20552:8080 或 0.0.0.0 绑定
- 启动并验收：curl -sI http://127.0.0.1:20552 返回 200/302
- 若 ghcr.io 拉取失败，先加镜像加速或重试，仍失败则停下来告诉我，不要换成来历不明的镜像
- 提醒我登录后台把默认口令 admin/admin 改掉

==================== 第二步：安装并配置 nginx ====================
- 安装 nginx（apt install -y nginx），停用默认站点（删 sites-enabled/default 软链）
- 计算证书文件权限：私钥 chmod 600 root:root，crt chmod 644
- 新建 /etc/nginx/sites-enabled/camouflage，内容要点：
  server {
      listen 0.0.0.0:8443 ssl http2;
      server_name <域名>;
      ssl_certificate     <crt 路径>;
      ssl_certificate_key <key 路径>;
      ssl_protocols TLSv1.2 TLSv1.3;
      ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
      ssl_prefer_server_ciphers off;
      ssl_session_timeout 1d;
      ssl_session_cache shared:SSL:50m;
      client_max_body_size 32m;

      location /<隐藏路径>/ {
          auth_basic "Restricted";
          auth_basic_user_file /etc/nginx/.htpasswd_xui;
          proxy_pass https://127.0.0.1:<webPort>;
          proxy_ssl_verify off;
          proxy_http_version 1.1;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection "upgrade";
          proxy_connect_timeout 60s;
          proxy_send_timeout 3600s;
          proxy_read_timeout 3600s;
      }

      location / {
          proxy_pass http://127.0.0.1:20552;
          proxy_http_version 1.1;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection "upgrade";
          proxy_connect_timeout 60s;
          proxy_send_timeout 60s;
          proxy_read_timeout 60s;
      }
  }
- location 的隐藏路径必须首尾都带斜杠，且与 3x-ui 的 webBasePath 完全一致（这是最容易翻车的点）
- 若 8443 已被占用，先告诉我被谁占用，不要随手换端口
- nginx -t 通过后才 reload
- 可选增强：若要让日志和 WAF 看到真实客户端 IP，在 http{} 内加
  set_real_ip_from <Cloudflare 官方 IP 段>;
  real_ip_header CF-Connecting-IP;
  并说明 CF 的 IP 段需要从官方页面获取，不要在配置里写死猜测的网段

==================== 第三步：basic auth ====================
- 生成 /etc/nginx/.htpasswd_xui：htpasswd -c -B 或 openssl passwd -apr1（若无 apache2-utils 就用 openssl）
- 用户名只用字母数字下划线，密码 12 位以上
- chmod 640，属主 root:www-data（ubuntu/debian 的 nginx 用户为 www-data）
- 不要在命令行明文密码后忘记清理 history

==================== 第四步：3x-ui 对齐 ====================
- webPort 改成 nginx proxy_pass 里的同一个端口（例：9266）
- webBasePath 必须填成 /<隐藏路径>/ —— 结尾斜杠不能少
- 面板证书指向同一份 Origin CA 的 crt/key
- 监听地址必须是 127.0.0.1；若当前面板版本没有「监听 IP」选项，
  告诉我，改用数据库或启动参数方式处理，并用 ss -tlnp 验证实际绑定，不要假设已生效
- 改完重启 x-ui 服务（systemctl restart x-ui），确认面板能正常打开

==================== 第五步：防火墙（最危险的一步） ====================
- 动手前先确认 SSH 端口（默认 22），并**先放行 SSH 再开启防火墙**
- 放行：22、80、443、8443
- 禁止放行：3x-ui 的 webPort、20552
- 若 ufw 尚未启用，先 ufw allow 22 再 ufw enable；执行后立刻另开一个 SSH 会话验证仍能登录
- 严禁修改 sshd_config、严禁改 SSH 端口、严禁执行会断开当前 SSH 的操作

==================== 第六步：验收（逐条执行并贴出原始输出） ====================
a) curl -sI http://127.0.0.1:20552                          预期 200/302
b) curl -skI https://127.0.0.1:8443/                         预期 200，且返回 LightNVR 相关响应头
c) curl -skI https://127.0.0.1:8443/<隐藏路径>/               预期 401
d) curl -skI -u <用户名>:<密码> https://127.0.0.1:8443/<隐藏路径>/  预期 200 或 302（进入面板）
e) curl -skI https://127.0.0.1:8443/<随机串>/                 预期 200（落到伪装站）而不是面板
f) ss -tlnp | grep -E "<webPort>|20552|8443"                 确认前两个只绑 127.0.0.1
g) openssl s_client -connect 127.0.0.1:8443 -servername <域名> </dev/null 2>/dev/null | openssl x509 -noout -subject -dates
   确认证书域名与有效期正确
h) 从外网 curl -I https://<域名>/<隐藏路径>/ （经 Cloudflare）确认返回 401 而不是 52x

==================== 硬性约束 ====================
- 禁止把 3x-ui 端口、20552 暴露公网
- 禁止使用 admin/admin、123456 之类弱口令
- 隐藏路径、basic auth 密码、面板密码、SSH 密码四者必须互不相同
- 不要复用旧机器导出的分享链接和订阅，入站重开一套
- 所有改动完成后输出：改动文件清单、回滚命令、端口占用表
- 不要删除 /etc/nginx/sites-enabled/default 之外的任何已有配置，删除前先备份
```

---

## 六、Cloudflare 那边要改什么

域名不变的情况下，改动很小：

1. **DNS**：A 记录从旧 IP 改成新 IP，代理状态保持「已代理（橙云）」。
2. **SSL/TLS 模式**：`Full (strict)`。因为源站是 Origin CA 证书，不能用 Flexible。
3. **端口**：8443 属 Cloudflare 支持的 HTTPS 端口，无需特殊开通；但要确认回源走的是 8443（若想让 CF 回源 443，则 nginx 要改成 listen 443，这与「面板藏 8443」是两种取向）。
4. **WAF 规则（第一层防线）**：给 `URI Path contains /kjJLZrSlkDxHsHwl4RoD7I/` 加一条规则，`IP Source Address not in {自己的 IP}` → Block。这样别人连 basic auth 弹窗都看不到。免费版规则条数有限（约 5 条），优先保这一条。
5. **安全建议**：
   - 关掉 `Always Use HTTPS` 之外的自动改写，避免 301 把隐藏路径跳到根域名
   - 关闭 Rocket Loader / Email Obfuscation，防止注入脚本破坏面板前端
   - 面板路径不要出现在 CF 的缓存规则里
   - 家宽/公司 IP 会变，WAF 白名单建议用「邮箱验证的正则」或定期更新，别写死后忘记
6. **可选进阶**：改用 Cloudflare Tunnel（cloudflared），源站完全不开放入站端口，IP 彻底隐藏。代价是 nginx 需要按 Host + Path 分流，且回国线路可能更慢。

---

## 七、坑位提醒

- `webBasePath` 与 nginx location 少一个斜杠就会 404，这是最常见的失败原因。
- 面板 WebSocket 断线多半是 `Connection "upgrade"` 或 `proxy_read_timeout` 没配。
- `proxy_ssl_verify off` 在使用 Origin CA 证书时通常需要，否则 502。
- LightNVR 容器内存上限 512m，2C4G 机器上和 3x-ui 共存没问题，但别再堆服务。
- 迁移后建议重开一套新的入站与订阅，别把旧机器的分享链接直接复用。
- 本目录含密码哈希与初始口令，属于敏感文件，不要提交到任何公开仓库。
- `ufw enable` 之前务必先放行 22，这是最经典的把自己锁在门外。
- 3x-ui 老版本面板设置页可能没有「监听 IP」，只改 webPort/webBasePath，实际绑定要靠 `ss -tlnp` 复核。
- Cloudflare 橙云下 `curl` 直连源站 IP 测不到真实效果，验收要分别测「本机直连」和「经 CF 访问」两条链路。
- Origin CA 证书有效期默认 15 年，但域名迁移/更换时必须重新签发。

---

## 八、最小回滚方案

```bash
# 停伪装站
docker compose -f /opt/lightnvr/docker-compose.yml down

# 撤 nginx 站点
rm -f /etc/nginx/sites-enabled/camouflage && nginx -t && systemctl reload nginx

# 关掉 8443
ufw delete allow 8443/tcp

# 3x-ui 端口/路径改回原值后
systemctl restart x-ui
```

> 回滚前先备份 `/etc/nginx/sites-enabled/camouflage` 和 `/etc/x-ui/x-ui.db`。
