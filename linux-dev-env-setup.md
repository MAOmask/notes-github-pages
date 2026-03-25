# Windows 开发环境搭建指南

> 使用 brew + Mise 搭建统一的 Linux 开发环境

***

> 终端美化配置
  ```bash
  # 克隆仓库
  git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf

  # 运行安装脚本（会询问是否启用快捷键）
  ~/.fzf/install
  ```

## 一、安装 brew（包管理器）

### 1.1 下载并安装

以 root 身份运行：

```bash
apt update
useradd -m -s /bin/bash linuxbrew
usermod -aG sudo linuxbrew
mkdir -p /home/linuxbrew/.linuxbrew
chown -R linuxbrew:linuxbrew /home/linuxbrew/.linuxbrew
su - linuxbrew -c '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
(echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> ~/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
# 1. 找到真正的 brew，把它改名叫 brew_real
if [ -f /home/linuxbrew/.linuxbrew/bin/brew ] && [ ! -f /home/linuxbrew/.linuxbrew/bin/brew_real ]; then
    mv /home/linuxbrew/.linuxbrew/bin/brew /home/linuxbrew/.linuxbrew/bin/brew_real
fi
# 2. 在原来的位置创建一个聪明的替身脚本
cat <<EOF > /home/linuxbrew/.linuxbrew/bin/brew
#!/bin/bash
if [ "\$(id -u)" -eq 0 ]; then
    # 如果是 root 用户，切换到 linuxbrew 执行真正的 brew_real
    su - linuxbrew -c "/home/linuxbrew/.linuxbrew/bin/brew_real \$*"
else
    # 如果是普通用户，直接执行真正的 brew_real
    /home/linuxbrew/.linuxbrew/bin/brew_real "\$@"
fi
EOF
# 3. 给这个脚本赋予执行权限，并把所有权给 linuxbrew 用户
chmod +x /home/linuxbrew/.linuxbrew/bin/brew
chown linuxbrew:linuxbrew /home/linuxbrew/.linuxbrew/bin/brew
# 4. 验证一下是否成功（如果显示 linuxbrew，那就对了！）
ls -l /home/linuxbrew/.linuxbrew/bin/brew
```

非root用户：

```bash
# 使用官方脚本安装
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 1.2 新电脑快速配置

换了新电脑，如何一键恢复所有 brew 软件？

```
# 导出已安装软件列表
brew bundle dump --file=~/Brewfile
```

```
# 在新电脑上恢复
brew bundle --file=~/Brewfile
```

### 1.3 常用 Homebrew 命令

| 命令 | 作用 |
| --- | --- |
| `brew install <package>` | 安装软件包 |
| `brew uninstall <package>` | 卸载软件包 |
| `brew search <keyword>` | 搜索软件包 |
| `brew list` | 列出已安装的软件 |
| `brew update` | 更新 Homebrew 本身 |
| `brew upgrade` | 升级所有软件包 |
| `brew cleanup` | 清理旧版本 |
| `brew bundle dump` | 导出已安装软件列表到 Brewfile |
| `brew bundle` | 从 Brewfile 安装软件 |

***

## 二、安装 Mise（运行时版本管理器）

### 2.1 安装 Mise

```bash
brew install mise
```

### 2.2 配置 Shell 配置文件

编辑 ~/.bashrc 配置文件，添加以下内容：

```bash
# Mise 初始化
eval "$(mise activate bash)"  
```

如果使用 zsh，改为：

```zsh
eval "$(mise activate zsh)"  
```


### 2.3 重新加载配置

```bash
source ~/.bashrc
```

***

## 三、使用 Mise 管理项目环境

### 3.1 进入项目目录

```bash
cd <你的项目路径>
```

### 3.2 安装项目所需的工具

```bash
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

```bash
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

```bash
# 列出已安装的工具
mise list

# 检查 Mise 状态
mise doctor
```

***

## 四、常用 Mise 命令

| 命令                                | 作用           |
| --------------------------------- | ------------ |
| `mise use <tool>@<version>`       | 当前目录安装指定版本   |
| `mise use -g <tool>@<version>`    | 全局安装         |
| `mise list`                       | 查看已安装的工具     |
| `mise list <tool>`                | 查看指定工具的已安装版本 |
| `mise uninstall <tool>@<version>` | 卸载指定版本       |
| `mise uninstall <tool>`           | 卸载所有版本       |
| `mise prune`                      | 清理未使用的版本     |
| `mise doctor`                     | 诊断检查         |
| `mise current`                    | 查看当前激活的工具    |

***

## 五、核心要点

### 5.1 常见问题与解决方案

| 问题                             | 解决方案                                      |
| ------------------------------ | ----------------------------------------- |
| Administrator 无法安装 Scoop       | 使用 `.\install.ps1 -RunAsAdmin` 参数         |
| Oh My Posh 用户不需要 PSCompletions | 跳过 `psc` 相关步骤，直接配置 Profile                |
| `mise` 命令找不到                   | 确保 `$PROFILE` 中添加了 PATH 和 `mise activate` |
| `rust` 命令找不到                   | 正确命令是 `rustc` 或 `cargo`，不是 `rust`         |
| 多项目版本冲突                        | Mise 自动通过 `mise.toml` 切换，不会混乱             |
| 切换目录后工具版本没变                    | 确保已进入包含 `mise.toml` 的目录                   |
| 新安装的命令找不到                      | 重启终端或执行 `. $PROFILE` 重新加载配置               |

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

***

## 六、参考资源

- [Scoop 官网](https://scoop.sh)
- [Mise 文档](https://mise.jdx.dev)
- [Oh My Posh 文档](https://ohmyposh.dev)
- [原始教程](https://blog.zsdy.dev/posts/building-a-windows-development-environment-with-scoop-and-mise)

