# Windows 开发环境搭建指南

> 使用 Scoop + Mise + Oh My Posh 搭建统一的 Windows 开发环境

---

## 一、安装 Scoop（包管理器）

### 1.1 下载并安装

以 Administrator 身份运行 PowerShell：

```powershell
# 设置执行策略，允许本地脚本运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 下载安装脚本
Invoke-WebRequest -Uri https://get.scoop.sh -OutFile install.ps1

# 使用 -RunAsAdmin 参数执行（Administrator 用户必需）
.\install.ps1 -RunAsAdmin
```

### 1.2 添加软件库（Bucket）

```powershell
# main: Scoop 官方默认库，包含经过严格审查的开源 CLI 工具
scoop bucket add main

# extras: 包含大量非 CLI 的常用软件
scoop bucket add extras

# versions: 如果你需要旧版本的软件
scoop bucket add versions
```

### 1.3 配置多线程下载（可选但推荐）

```powershell
# 安装 Aria2
scoop install aria2

# 启用多线程下载
scoop config aria2-enabled true
scoop config aria2-max-connection-per-server 16
scoop config aria2-split 16
```

---

## 二、安装 Mise（运行时版本管理器）

### 2.1 安装 Mise

```powershell
scoop install mise
```

### 2.2 配置 PowerShell Profile

编辑 PowerShell 配置文件：

```powershell
notepad $PROFILE
```

添加以下内容：

```powershell
# 确保 Mise 和 Scoop 在 PATH 中
$env:PATH = "$env:USERPROFILE\scoop\shims;$env:USERPROFILE\AppData\Local\mise\shims;$env:PATH"

# 初始化 Mise（关键！）
$env:MISE_SHELL = "pwsh"
Invoke-Expression (&mise activate pwsh | Out-String)
```

### 2.3 重新加载配置

```powershell
. $PROFILE
```

---

## 三、使用 Mise 管理项目环境

### 3.1 进入项目目录

```powershell
cd <你的项目路径>
```

### 3.2 安装项目所需的工具

```powershell
# 安装 Node.js
mise use node@20

# 安装 Rust
mise use rust@stable

# 安装 Python
mise use python@3.12

# 安装 Go
mise use go@1.23
```

执行后会在当前目录生成 `mise.toml` 配置文件。

### 3.3 验证安装

```powershell
# Node.js
node --version

# Rust（注意：Rust 的命令是 rustc，不是 rust）
rustc --version
cargo --version

# Python
python --version

# Go
go version
```

### 3.4 查看当前配置

```powershell
# 列出已安装的工具
mise list

# 检查 Mise 状态
mise doctor
```

---

## 四、常用 Mise 命令

| 命令 | 作用 |
|------|------|
| `mise use <tool>@<version>` | 当前目录安装指定版本 |
| `mise use -g <tool>@<version>` | 全局安装 |
| `mise list` | 查看已安装的工具 |
| `mise list <tool>` | 查看指定工具的已安装版本 |
| `mise uninstall <tool>@<version>` | 卸载指定版本 |
| `mise uninstall <tool>` | 卸载所有版本 |
| `mise prune` | 清理未使用的版本 |
| `mise doctor` | 诊断检查 |
| `mise current` | 查看当前激活的工具 |

---

## 五、核心要点

### 5.1 常见问题与解决方案

| 问题 | 解决方案 |
|------|---------|
| Administrator 无法安装 Scoop | 使用 `.\install.ps1 -RunAsAdmin` 参数 |
| Oh My Posh 用户不需要 PSCompletions | 跳过 `psc` 相关步骤，直接配置 Profile |
| `mise` 命令找不到 | 确保 `$PROFILE` 中添加了 PATH 和 `mise activate` |
| `rust` 命令找不到 | 正确命令是 `rustc` 或 `cargo`，不是 `rust` |
| 多项目版本冲突 | Mise 自动通过 `mise.toml` 切换，不会混乱 |
| 切换目录后工具版本没变 | 确保已进入包含 `mise.toml` 的目录 |
| 新安装的命令找不到 | 重启终端或执行 `. $PROFILE` 重新加载配置 |

### 5.2 多项目版本管理

Mise 的核心优势是**自动版本切换**：

```
项目 A (mise.toml: node@18)
  └── cd 进入目录 → 自动使用 Node 18

项目 B (mise.toml: node@20)
  └── cd 进入目录 → 自动使用 Node 20

全局默认
  └── 不在项目目录 → 使用全局版本或未激活
```

### 5.3 团队环境统一

将 `mise.toml` 提交到 Git 仓库：

```toml
[tools]
node = "20"
rust = "stable"

[env]
NODE_ENV = "development"
```

新成员只需：

```powershell
git clone <repo>
cd <repo>
mise install
```

---

## 六、参考资源

- [Scoop 官网](https://scoop.sh)
- [Mise 文档](https://mise.jdx.dev)
- [Oh My Posh 文档](https://ohmyposh.dev)
- [原始教程](https://blog.zsdy.dev/posts/building-a-windows-development-environment-with-scoop-and-mise)

---

> 文档版本: 1.0
> 创建日期: 2026-03-19
> 适用系统: Windows 10/11 + PowerShell 7+
