
```
请帮我使用pkg工具将我的Node.js全栈应用（包含前端React和后端Express）打包成独立的Windows可执行文件。

项目结构：
- client/ (React前端)
- server/ (Express后端)
- image/ (应用图标)

要求：
1. 打包后的exe文件能独立运行，不需要安装Node.js环境
2. 双击exe文件后自动启动服务器并打开浏览器
3. 支持外部配置文件config.json来配置数据库连接
4. 使用自定义应用图标
5. 能正确处理文件路径和日志文件创建
6. 添加详细的错误输出和调试信息

具体步骤：
1. 创建主启动文件main.js，整合前后端启动逻辑
2. 配置package.json中的pkg打包参数
3. 处理pkg打包后的snapshot虚拟文件系统限制
4. 修改服务器代码以支持真实工作目录
5. 设置自定义图标和压缩选项
6. 创建用户使用说明文档

技术要点：
- 使用require()直接加载服务器模块而不是spawn子进程
- 通过环境变量REAL_WORK_DIR传递真实工作目录
- 处理日志文件和配置文件的路径问题
- 添加完善的错误处理和用户友好的提示信息

应用名称：用户行为分析系统
图标路径：image/analysing.ico
```

## 关键代码模板

如果您需要再次打包类似的全栈应用，这里是关键的代码模板：

### 1. 主启动文件 (main.js)

```javascript
#!/usr/bin/env node
const path = require('path');
const fs = require('fs');

// 全局错误处理
process.on('uncaughtException', (error) => {
  console.error('未捕获的异常:', error);
  console.log('按任意键退出...');
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.on('data', process.exit.bind(process, 1));
});

// 设置真实工作目录
const realWorkDir = path.dirname(process.execPath);
process.env.REAL_WORK_DIR = realWorkDir;
process.env.NODE_ENV = 'production';

// 配置文件处理...
// 服务器启动逻辑...
```

### 2. package.json配置

```json
{
  "main": "main.js",
  "bin": "main.js",
  "pkg": {
    "scripts": ["server/**/*.js", "main.js"],
    "assets": [
      "client/build/**/*",
      "server/config/**/*", 
      "image/**/*",
      "config.json"
    ],
    "targets": ["node18-win-x64"],
    "outputPath": "dist"
  }
}
```

### 3. 服务器代码修改

```javascript
// 使用真实工作目录
const realWorkDir = process.env.REAL_WORK_DIR || process.cwd();
let logDir = path.join(realWorkDir, 'logs');

// 安全的目录创建
if (!fs.existsSync(logDir)) {
  try {
    fs.mkdirSync(logDir, { recursive: true });
  } catch (error) {
    // 降级到临时目录
    logDir = path.join(require('os').tmpdir(), 'app-logs');
    fs.mkdirSync(logDir, { recursive: true });
  }
}
```

### 4. 打包命令

```bash
# 构建前端
cd client && npm run build && cd ..

# 安装依赖
npm install

# 打包为exe（带自定义图标）
pkg . --targets node18-win-x64 --output "dist/应用名称.exe" --compress GZip --icon "image/图标.ico"
```

## 常见问题解决方案

1. **"Cannot mkdir in a snapshot"错误**：使用 `process.env.REAL_WORK_DIR`设置真实工作目录
2. **"spawn ENOENT"错误**：使用 `require()`直接加载模块而不是 `spawn()`启动子进程
3. **路径问题**：区分 `__dirname`(snapshot路径)和 `process.cwd()`(真实路径)
4. **配置文件**：支持运行目录下的外部配置文件，便于用户自定义

