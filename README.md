# HelloCV

> 纳新培训任务仓库 —— Linux 系统基础与开发环境搭建、Git 版本控制工具、CMake 构建系统、LLM 决策网关、学习笔记索引
>
> 作者：**nailya**（GitHub: [@SuYouChiTa](https://github.com/SuYouChiTa)）　|　创建时间：2026-09-28

---

## 一、这是什么

本仓库是纳新培训任务的**提交仓库**，用于集中存放培训阶段的学习记录与语雀笔记入口。仓库本身不承载主要代码，重点在于：

1. 用 `README.md` 说明**仓库结构、环境配置步骤与使用方法**，让任何人都能快速了解本项目的组织方式；
2. 用 [`docs/notes-index.md`](docs/notes-index.md) 汇总培训期间的全部**语雀笔记链接**，方便查看完整学习记录（含截图与操作过程）。

培训任务包含两次任务、共四个部分，本仓库对应**第一部分（Linux）**、**第二部分（Git）**、**第三部分（CMake）**与**第四部分（LLM 决策网关）**，四部分均已完成：

| 部分 | 内容 | 状态 |
|---|---|---|
| 第一部分 | Linux 系统基础与开发环境搭建（安装 Ubuntu、配置系统、安装 IDE/ROS2/常用工具、学习记录） | 已完成 |
| 第二部分 | Git 版本控制工具（配置 Git 与 SSH 密钥、使用 Git 完成四则运算计算器开发，仓库 [`git_training`](https://gitee.com/yuwen-ling/git_training)） | 已完成 |
| 第三部分 | CMake 构建系统（单位转换器项目：根+库两个 CMakeLists、静态库与可执行文件、源码外构建，代码见 [`UnitConverter/`](UnitConverter/)） | 已完成 |
| 第四部分 | LLM 决策网关（补全网关骨架，与 LLM 进行石头剪刀布，使用 DeepSeek 官方 API，代码见 [`llm-gateway/`](llm-gateway/)） | 已完成 |

> 仓库名 `HelloCV` 沿用第一次任务的要求，实际作为三次培训任务的统一提交仓库使用。

---

## 二、仓库结构

```text
HelloCV/
├── README.md                  # 本文件：项目说明、环境配置步骤、Git 实践、CMake 实践、LLM 网关、使用方法
├── docs/
│   └── notes-index.md         # 语雀笔记链接汇总文档（培训要求项）
├── llm-gateway/               # 第四部分：LLM 决策网关实现（关键脚本）
│   ├── gateway/               #   补全后的网关代码（JSON 容错 / 规则兜底 / 上游通信 / 主流水线）
│   ├── run_gateway.py         #   一行进、一行出
│   └── play_game.py           #   与 LLM 对局演示
└── UnitConverter/             # 第三部分：CMake 单位转换器项目
    ├── CMakeLists.txt         #   根构建文件（工程定义 / 可执行文件 / 链接库 / 安装规则）
    ├── src/main.cpp           #   交互入口（菜单与输入输出）
    └── unitlib/               #   转换库（含第二个 CMakeLists.txt）
```

说明：

- `README.md`——仓库门面，介绍项目目的、结构与使用方式；
- `docs/notes-index.md`——**所有语雀笔记的链接汇总**，按培训主题分类（学习内容 / 实践任务）；
- `UnitConverter/`——第三部分的完整代码（含两个 `CMakeLists.txt`），按任务书要求的"（可选）关键脚本、配置文件等"提供；
- `llm-gateway/`——第四部分的关键脚本，同属"（可选）关键脚本、配置文件等"；
- 后续如有需要，可继续扩展 `docs/`（放置关键脚本、配置文件等）与 `assets/`（放置 README 引用的截图）。

---

## 三、环境配置步骤

以下为本人在培训中实际使用的环境与配置流程，供复现参考。完整过程（含截图、报错与解决方式）见 [`docs/notes-index.md`](docs/notes-index.md) 中的 Linux 学习与实践记录。

### 3.1 宿主机环境

| 项目 | 内容 |
|---|---|
| 操作系统 | Windows 11 家庭版 25H2（Build 26200.9457） |
| 处理器 / 内存 | AMD Ryzen 9 8945HX / 32GB RAM |
| 虚拟机软件 | VMware Workstation 17 Pro（17.6.3 build-24583834） |

### 3.2 虚拟机与操作系统

| 项目 | 内容 |
|---|---|
| 客户机系统 | Ubuntu 26.04.1 LTS（resolute）Desktop 桌面版，x86_64 |
| 内核版本 | 7.0.0-38-generic |
| 虚拟硬件 | 2 核 CPU / 内存 3.3GiB / 磁盘 40GB |
| 网络模式 | NAT，网卡 `ens33`，IP `192.168.164.128/24` |
| 用户名 / 主机名 | `nailya` / `naily-VMware-Virtual-Platform` |

> 安装思路：先装 VMware，再按 CPU 架构下载 Ubuntu Desktop AMD64 镜像新建虚拟机；安装时使用**简短的英文用户名与主机名**，并勾选安装 OpenSSH server，便于后续 SSH 练习。

### 3.3 系统初始化

```bash
# 更新软件包索引并升级
sudo apt update
sudo apt upgrade -y

# 安装编译、网络、版本控制与终端工具
sudo apt install nmap ssh git vim flex bison gcc g++ make cmake openssh-server tmux

# 安装 Node.js、npm 与 PM2
sudo apt install nodejs npm
sudo npm install -g pm2
```

若 npm 安装 pm2 时出现自签名证书错误（`DEPTH_ZERO_SELF_SIGNED_CERT`），可切换镜像源后重装：

```bash
npm config set registry https://registry.npmmirror.com
sudo npm install -g pm2
```

### 3.4 安装 VS Code 与 ROS2

```bash
# VS Code：从官网下载 .deb 包安装，验证
code --version

# ROS2（lyrical）：使用一键脚本安装
wget http://fishros.com/install -O fishros && . fishros

# 加载环境并验证
source /opt/ros/lyrical/setup.bash
printenv ROS_DISTRO          # 应输出 lyrical
ros2 doctor                  # 环境自检
```

为让环境在每次打开终端时自动生效，可将 source 命令写入 `~/.bashrc`：

```bash
echo "source /opt/ros/lyrical/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 3.5 远程连接配置（SSH 公钥登录）

```bash
# 在客户端生成密钥对（不设口令可直接回车两次）
ssh-keygen -t ed25519 -C "windows-host"

# 将公钥部署到目标主机（Linux 侧可用 ssh-copy-id）
ssh-copy-id nailya@192.168.164.128

# 验证：出现 Authenticated ... using "publickey" 即表示免密登录成功
ssh -v nailya@192.168.164.128 2>&1 | grep -Ei "publickey|Authenticated"
```

可选：在客户端 `~/.ssh/config` 中配置别名，简化登录与文件传输：

```text
Host vm
    HostName 192.168.164.128
    User nailya
    Port 22
    IdentityFile C:\Users\<用户名>\.ssh\id_ed25519
```

---

## 四、Git 版本控制实践（第二部分）

> 说明：以下为**第二部分（Git）**的记录；**第四部分（LLM 决策网关）**见第六节。

第二部分使用 Git 完成了一个 C++ 四则运算计算器的开发，仓库为 [`git_training`](https://gitee.com/yuwen-ling/git_training)（Gitee，公开）。核心流程如下：

### 4.1 基础配置与 SSH 密钥

```bash
# 配置提交身份
git config --global user.name "宇文凌"
git config --global user.email "你的邮箱"

# 生成密钥并把公钥添加到 Gitee（设置 → 安全设置 → SSH 公钥）
ssh-keygen -t ed25519 -C "github-SuYouChiTa"
cat ~/.ssh/id_ed25519.pub

# 验证（返回 Hi ... You've successfully authenticated 即成功）
ssh -T git@gitee.com
```

### 4.2 分支开发流程

```bash
git init
git branch -M main
git add .
git commit -m "chore: 初始化项目结构"
git remote add origin git@gitee.com:yuwen-ling/git_training.git
git push -u origin main

# 功能一：加减法（独立分支开发后合并）
git switch -c feature/add-sub
git add src/Calculator.cpp && git commit -m "feat: 实现加法与减法"
git switch main && git merge feature/add-sub

# 功能二：乘除法与取模（同样独立分支开发，用 --no-ff 保留合并记录）
git switch -c feature/mul-div
git add src/Calculator.cpp && git commit -m "feat: 实现乘法、除法与取模"
git switch main && git merge --no-ff feature/mul-div -m "merge: 合并乘除法分支到 main"
git push origin main && git push origin --all
```

### 4.3 编译运行

```bash
g++ -std=c++17 -Wall -o calc src/main.cpp src/Calculator.cpp -Isrc
./calc
```

### 4.4 要求与实践要点

| 项目 | 说明 |
|---|---|
| 提交次数 | 6 次（初始化、加减法、乘除法、`--no-ff` 合并、两次 `.gitignore` 修复） |
| 分支策略 | 加减法与乘除法分别在 `feature/add-sub`、`feature/mul-div` 上开发，再合并回 `main` |
| 合并方式对比 | 第一次为快进合并（历史成直线），第二次用 `--no-ff` 保留分叉与合并提交 |
| 忽略编译产物 | `.gitignore` 覆盖 `build/`、`*.o`、`*.exe`、`calc` 等；`git ls-files` 仅有 5 个源文件 |
| 关键命令 | `init`/`status`/`add`/`commit`/`branch`/`switch`/`merge`/`stash`/`stash pop`/`push`/`pull`/`log` |

---

---

## 五、CMake 构建实践（第三部分）

第三部分用 CMake 组织了一个"单位转换器"项目。**重点不是换算功能，而是构建系统本身**：把换算逻辑做成一个库、把交互做成一个可执行文件，用两个 `CMakeLists.txt` 分别描述，模拟真实项目的多目标结构。

### 5.1 项目结构

```text
UnitConverter/
├── CMakeLists.txt              # 根：工程定义 + 可执行文件 + 链接库 + 安装规则
├── src/
│   └── main.cpp                # 交互逻辑（菜单、方向、数值）
├── unitlib/                    # 转换库
│   ├── CMakeLists.txt          # 库：add_library + 导出 include 目录
│   ├── include/unitlib.h       # 对外接口（只有声明）
│   └── src/unitlib.cpp         # 换算实现（6 个函数）
└── build/                      # 编译目录（自行创建，不提交）
```

### 5.2 构建流程（源码外构建）

```bash
cd UnitConverter
mkdir build && cd build
cmake ..        # 配置期：解析 CMakeLists，生成构建文件
make            # 构建期：编译 + 链接
./unitconv      # 运行
```

Windows 下用 MinGW 时必须显式指定生成器（默认会去找 MSVC），产物为 `unitconv.exe`：

```powershell
cmake -S . -B build -G "MinGW Makefiles"
cmake --build build
```

`make` 的输出能直接看出两个 CMakeLists 的分工：

```text
[ 25%] Building CXX object unitlib/CMakeFiles/unitlib.dir/src/unitlib.cpp.o
[ 50%] Linking CXX static library libunitlib.a
[ 50%] Built target unitlib
[ 75%] Building CXX object CMakeFiles/unitconv.dir/src/main.cpp.o
[100%] Linking CXX executable unitconv
[100%] Built target unitconv
```

### 5.3 实践要点

| 项目 | 说明 |
|---|---|
| 目标划分 | `unitlib`（静态库 `libunitlib.a`）+ `unitconv`（可执行文件）；根 CMakeLists 用 `add_subdirectory(unitlib)` 引入库目标 |
| 头文件传递 | `target_include_directories(unitlib PUBLIC include)`——链接 `unitlib` 的目标自动获得头文件路径；写成 `PRIVATE` 则报 `fatal error: unitlib.h: 没有那个文件或目录` |
| 链接 | `target_link_libraries(unitconv PRIVATE unitlib)`：一行同时完成"链接库"与"继承 PUBLIC 头文件目录" |
| 功能 | 摄氏度↔华氏度、米↔英尺、千克↔磅，三组双向换算；菜单交互；非法输入有保护 |
| 产物位置 | 静态库在 `build/unitlib/libunitlib.a`，可执行文件在 `build/unitconv`；`.gitignore` 已忽略 `build/` |
| 可选命令 | `find_package(Threads REQUIRED)`、`install(...)` + `cmake --install build --prefix ...` 验证 |
| 错误分辨 | 配置期 `CMake Error`（语法/缓存）；编译期 `fatal error: xxx.h`（找不到头文件）；链接期 `undefined reference to ...`（找不到实现） |

> 详细笔记见语雀 [《CMake学习内容笔记》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/onlt3g6pviouww59?singleDoc#) 与 [《CMake实践任务笔记》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/ckpfnfs0gsgi98lg?singleDoc#)。
## 六、LLM 决策网关实践（第四部分）

第三部分补全了一个"网关"程序：**本地程序与外部大模型之间的中间服务**——把本地输入整理成便于发送的格式，再把模型输出整理成便于本地程序接收、存储、调用的格式。网关运行期间的硬性约定是**一行进、一行出**：

| | 内容 |
|---|---|
| 输入 | 每行一个 JSON：`{"time": "<本轮时间>", "history": ["rock", "paper"]}`（`history` 可选） |
| 输出 | 每行一个 JSON：`{"time": "<与输入一致>", "option": "rock\|scissor\|paper"}` |
| 不变式 | 坏输入、上游故障、模型输出脏格式，都必须回一行**合法 JSON**，绝不抛异常 |

### 6.1 代码结构（`llm-gateway/`）

```text
llm-gateway/
├── gateway/
│   ├── json_guard.py     # JSON 容错层：剥 markdown 围栏 / 字符串感知的括号配对 / 文本级修复
│   ├── rules.py          # 决策规则层：取值归一化 / 校验修正 / 本地兜底
│   ├── client.py         # 上游通信层：组装请求体 / 分类重试 / 只取 content
│   ├── app.py            # 主流水线：把上面各层串起来
│   ├── config.py         # 配置：模型、超时、重试次数、API Key 来源
│   ├── prompts.py        # 预设提示词（system / user）
│   └── game.py           # 对局与胜负判定
├── run_gateway.py        # 一行进、一行出
└── play_game.py          # 与 LLM 对局演示
```

分层原则：**格式问题在容错层解决，语义问题在规则层解决**。

### 6.2 运行步骤

```bash
# 1) 依赖：requests（HTTP 客户端）
pip install -r requirements.txt

# 2) API Key 通过环境变量提供，不写进代码
#    Windows PowerShell:
setx DEEPSEEK_API_KEY "sk-你的key"
#    Linux / macOS:
export DEEPSEEK_API_KEY=sk-你的key

# 3) 离线跑通流水线（不调用 API、不花钱）
echo '{"time":"2026-01-01T00:00:00+00:00"}' | python run_gateway.py --offline

# 4) 与真实 DeepSeek 对局 6 局（--seed 让对手出拳可复现）
python play_game.py --rounds 6 --seed 42

# 5) 用本地假上游压测容错能力（故意返回围栏/废话/非法取值/空回复）
python mock_llm_server.py --port 8801 &
python play_game.py --rounds 6 --api-base-url http://127.0.0.1:8801 --api-key test
```

### 6.3 实践要点

| 项目 | 说明 |
|---|---|
| 上游 | **DeepSeek 官方 API**（OpenAI 兼容的 `/chat/completions`），开启 `response_format=json_object`，默认关闭思考模式 |
| 容错三级 | 剥围栏 → 字符串感知的括号配对 → 文本级修复（去注释/换字面量/去尾随逗号/统一引号/补齐括号），全程不使用 `eval` |
| 重试策略 | 401/403/400 **立刻失败**（确定性错误，重试无意义）；429/5xx、网络异常、空回复**指数退避重试**（并遵守服务端 `Retry-After`） |
| 可信边界 | 输出的 `time` **一律以请求为准**，不采信模型自己写的时间；`history` 只作为提示词上下文，不作为答案 |
| 兜底保障 | 上游完全不可用时，本地规则反制对手上一手，保证仍能输出合法决策 |
| 验证 | 单元测试 **93 项全部通过**；真实 API 对局 6 轮全部 HTTP 200；假上游压测 6 轮零中断 |

> 详细的实现思路、10 个函数的职责、踩坑与验证过程，见语雀笔记 [《LLM网关-AI协作学习记录》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/hp723ckq1xvl1txf?singleDoc#)。

---

## 七、使用方法

1. **了解培训内容**：先阅读本文件的"环境配置步骤"（Linux 部分）、"LLM 决策网关实践"（LLM 部分）与"Git 版本控制实践"（Git 部分），了解所需的软硬件与操作流程；
2. **查看完整学习记录**：打开 [`docs/notes-index.md`](docs/notes-index.md)，其中列出全部语雀笔记链接，按主题分类；
3. **复现环境**：按第三节的命令顺序执行（顺序为：系统更新 → 常用工具 → Node/npm/PM2 → VS Code/ROS2 → SSH 配置）；
4. **复现 LLM 网关**：按第六节 6.2 的步骤配置 API Key 并运行；离线模式不需要 Key，可先跑通流水线。关键脚本见 [`llm-gateway/`](llm-gateway/)；
5. **复现 Git 实践**：按第四节的流程创建分支、开发、合并并推送；配套代码见 [`git_training`](https://gitee.com/yuwen-ling/git_training)；
6. **复现 CMake 实践**：进入 `UnitConverter/`，`mkdir build && cd build && cmake .. && make`（Windows 下用 `cmake -S . -B build -G "MinGW Makefiles"`）；代码见 [`UnitConverter/`](UnitConverter/)；
7. **核对结果**：每条命令的预期输出与验证方式，均记录在对应的语雀笔记中（含终端截图）；
8. **遇到问题**：各篇笔记末尾整理了培训期间遇到的报错（Linux 15 类、Git 15 类、CMake 8 类，LLM 部分见"踩坑与解决汇总"一节）及其原因与解决办法，可先在那里检索。

---

## 八、学习内容一览

本阶段覆盖的知识点（详细内容见语雀笔记）：

| 分类 | 内容 |
|---|---|
| 系统安装 | VMware 虚拟机、Ubuntu 安装、磁盘扩容、NAT 网络模式 |
| 基础命令 | `apt`/`snap` 软件管理；`ls`/`cp`/`mv`/`rm`/`touch` 文件管理；`grep` 文本搜索 |
| 文件系统 | 根目录 `/`、`/home`、`/etc`、`/var` 等目录作用；绝对路径 vs 相对路径 |
| 权限管理 | `chmod`、`chown`、`ls -l` 权限位与数字表示法 |
| 进程与服务 | `ps`、`kill`、`top`、`systemctl`、`journalctl` 与 systemd 服务管理 |
| 工具入门 | Vim（三种模式）、tmux（会话/窗口/窗格）、`sed`、`awk` |
| 远程连接 | SSH 登录、主机密钥与用户密钥、`ssh-keygen` 公钥登录、`~/.ssh/config`、`scp` 传输 |
| 开发环境 | VS Code、GCC/G++/CMake 工具链、Node.js/npm/PM2、ROS2（lyrical） |
| 版本控制 | Git 三大区域、分支开发与合并（含 `--no-ff`）、`git stash`、远程同步（`push`/`pull`/`rebase`）、`.gitignore` 与编译产物管理、Pull Request 流程 |
| CMake 构建 | 目标（可执行文件 / 静态库）、两个 CMakeLists 的分工、`PUBLIC`/`PRIVATE` 传递依赖、源码外构建、`find_package`、`install`、配置期 / 编译期 / 链接期错误的分辨 |
| LLM 与 Agent | 大模型与 Agent 的关系、Chat Completions 协议、JSON 输出模式与提示词要求、模型输出的不可信性与容错、HTTP 重试策略分类、网关作为"可信边界"的设计 |

---

## 九、备注

- 仓库内所有命令均在 Ubuntu 26.04.1 LTS（ROS 2 `lyrical`）、Windows Git Bash 与 Windows PowerShell 环境中实际执行并验证；
- 培训任务书写作时的推荐版本为 Ubuntu 22.04，实际安装 26.04.1 LTS 的原因与差异已记录在对应笔记中；
- Git 实践任务的代码仓库为 [`git_training`](https://gitee.com/yuwen-ling/git_training)（Gitee，公开）；
- CMake 实践任务的代码在本仓库 [`UnitConverter/`](UnitConverter/) 中，Linux 下用 GCC + CMake 4.2.3 构建，Windows 下用 MinGW + `-G "MinGW Makefiles"`；
- LLM 决策网关的代码在本仓库 [`llm-gateway/`](llm-gateway/) 中，上游为 DeepSeek 官方 API；
- 引用网络教程之处均已标注来源；
- 仓库保持**公开**，便于评阅；如发现链接无法访问，请通过 Issues 告知。
