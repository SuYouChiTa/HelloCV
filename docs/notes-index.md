# 语雀笔记索引（notes-index）

> 本文件汇总纳新培训期间撰写的全部语雀笔记链接。
>
> 作者：nailya　|　最后更新：2026-10-10

---

## 一、使用说明

- 本索引按培训内容分类，每篇笔记均对应"**学习内容**"与"**实践任务**"两部分要求；
- 所有链接均为**公开可访问**（无需登录语雀即可查看）；
- 笔记中包含命令、运行结果截图、遇到的问题与解决办法，可直接作为学习记录查阅。

---

## 二、笔记清单

### 2.1 Linux 系统基础与开发环境搭建

| 序号 | 笔记标题 | 类型 | 内容概要 | 链接 |
|---|---|---|---|---|
| 1 | Linux 学习与实践记录 | 学习内容 + 实践任务 | 环境信息、Ubuntu 安装与配置、常用工具/VS Code/ROS2/PM2 安装验证、基础命令、权限与进程管理、Vim/tmux 入门、SSH 公钥登录与 scp 传输、grep/sed/awk、踩坑汇总 | [《linux学习与实践记录》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/sdt25tbsr1t0abfk?singleDoc#) |

> **说明**：该笔记对应任务"（一）Linux"的全部要求，包含：
> 1. **学习内容**：终端命令（apt/snap、cp/mv/rm/ls/touch、chmod/chown/ls -l、ps/kill/top/systemctl）、"Linux 中一切皆文件"的理解、文件系统结构（`/`、`/home`、`/etc`、`/var`）、绝对路径与相对路径、systemd 服务管理与网络配置、vim/tmux/grep/sed/awk；
> 2. **实践任务**：安装 Ubuntu、配置系统（换源/输入法/网络）、安装 IDE 与 ROS2 及常用工具、验证结果与问题解决过程。

### 2.2 Git 版本控制工具

| 序号 | 笔记标题 | 类型 | 内容概要 | 链接 |
|---|---|---|---|---|
| 2 | Git 学习内容笔记 | 学习内容 | Git 的作用、工作区/暂存区/仓库三大区域、常用命令与理解、`fetch` 与 `pull` 的区别、合并冲突解决、Rebasing 工作流、Pull Request 流程、易混淆点整理 | [《Git学习内容笔记》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/gf8gpefqc1x9nfbs?singleDoc#) |
| 3 | Git 实践任务笔记 | 实践任务 | 仓库 `git_training`（Gitee）、SSH 密钥与用户配置、计算器开发全过程、加减法分支与乘除法分支的开发及合并、`git stash` 练习、远程同步、编译产物与 `.gitignore` 处理、踩坑汇总 | [《Git实践任务笔记》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/wn8ykilgifqw8x6p?singleDoc#) |

> 说明：两篇笔记分别对应任务"学习内容"与"实践任务"的要求，实践任务配套代码仓库为 [gitee.com/yuwen-ling/git_training](https://gitee.com/yuwen-ling/git_training)（公开）。

---

## 三、相关仓库

| 仓库 | 说明 | 链接 |
|---|---|---|
| HelloCV | 本仓库：培训任务提交仓库，含 README 与笔记索引 | https://github.com/SuYouChiTa/HelloCV |
| git_training | Git 实践任务：C++ 四则运算计算器开发（Gitee 仓库，含加减法/乘除法分支开发与合并记录） | https://gitee.com/yuwen-ling/git_training |

---

## 四、备注

- 笔记中的命令均在实际环境（VMware + Ubuntu 26.04.1 LTS + ROS 2 `lyrical`；Windows Git Bash + Gitee 远程仓库）中执行并验证；
- 若某个链接无法访问，可能是语雀的公开权限设置问题，请通过 Issues 反馈；
- 引用网络资料之处已在笔记中标注来源。
