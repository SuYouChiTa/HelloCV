# HelloCV

> 纳新培训任务仓库 —— Linux 系统基础与开发环境搭建、学习笔记索引
>
> 作者：**nailya**（GitHub: [@SuYouChiTa](https://github.com/SuYouChiTa)）　|　创建时间：2026-09-28

---

## 一、这是什么

本仓库是纳新培训任务的**提交仓库**，用于集中存放培训阶段的学习记录与语雀笔记入口。仓库本身不承载主要代码，重点在于：

1. 用 `README.md` 说明**仓库结构、环境配置步骤与使用方法**，让任何人都能快速了解本项目的组织方式；
2. 用 [`docs/notes-index.md`](docs/notes-index.md) 汇总培训期间的全部**语雀笔记链接**，方便查看完整学习记录（含截图与操作过程）。

培训任务包含两部分内容，本仓库目前对应**第一部分（Linux）**：

| 部分 | 内容 | 状态 |
|---|---|---|
| 第一部分 | Linux 系统基础与开发环境搭建（安装 Ubuntu、配置系统、安装 IDE/ROS2/常用工具、学习记录） | 已完成 |
| 第二部分 | Git 版本控制工具（配置 Git、使用 Git 完成计算器开发，仓库 `git_training`） | 进行中 |

---

## 二、仓库结构

```text
HelloCV/
├── README.md                  # 本文件：项目说明、环境配置步骤、使用方法
└── docs/
    └── notes-index.md         # 语雀笔记链接汇总文档（培训要求项）
```

说明：

- `README.md`——仓库门面，介绍项目目的、结构与使用方式；
- `docs/notes-index.md`——**所有语雀笔记的链接汇总**，按培训主题分类（学习内容 / 实践任务）；
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

## 四、使用方法

1. **了解培训内容**：先阅读本文件的"环境配置步骤"，了解所需的软硬件与安装流程；
2. **查看完整学习记录**：打开 [`docs/notes-index.md`](docs/notes-index.md)，其中列出全部语雀笔记链接，按主题分类；
3. **复现环境**：按第三节的命令顺序执行（顺序为：系统更新 → 常用工具 → Node/npm/PM2 → VS Code/ROS2 → SSH 配置）；
4. **核对结果**：每条命令的预期输出与验证方式，均记录在对应的语雀笔记中（含终端截图）；
5. **遇到问题**：Linux 学习记录末尾整理了培训期间遇到的 15 类报错及其原因与解决办法，可先在那里检索。

---

## 五、学习内容一览

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

---

## 六、备注

- 仓库内所有命令均在 Ubuntu 26.04.1 LTS（ROS 2 `lyrical`）环境中实际执行并验证；
- 培训任务书写作时的推荐版本为 Ubuntu 22.04，实际安装 26.04.1 LTS 的原因与差异已记录在对应笔记中；
- 引用网络教程之处均已标注来源；
- 仓库保持**公开**，便于评阅；如发现链接无法访问，请通过 Issues 告知。
