# 语雀笔记索引（notes-index）

> 本文件汇总纳新培训期间撰写的全部语雀笔记链接。
>
> 作者：nailya　|　最后更新：2026-10-17

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

### 2.3 LLM 决策网关

| 序号 | 笔记标题 | 类型 | 内容概要 | 链接 |
|---|---|---|---|---|
| 4 | LLM网关-AI协作学习记录 | 学习内容 + 实践任务 | 为什么选 DSH 做 Agent 平台、与 AI 协作补全网关的完整过程（拆解任务 / 逐个实现 / 三轮测试收敛 / 真实 API 验证）、10 个函数分别起什么作用（附 C++ 类比）、运行验证与截图、踩坑与解决汇总 | [《LLM网关-AI协作学习记录》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/hp723ckq1xvl1txf?singleDoc#) |

> **说明**：该笔记对应任务"（三）LLM"的实践任务要求——在 Agent 帮助下补全 `/skeleton`，完成与 LLM 进行石头剪刀布的目标。包含：
> 1. **学习内容**：LLM 与 Agent 的关系、Chat Completions 协议、JSON 输出模式与提示词要求、模型输出为什么不可信、HTTP 重试策略分类、网关作为"可信边界"的设计原则；
> 2. **实践任务**：补全 JSON 容错层 / 决策规则层 / 上游通信层 / 主流水线共 10 个函数，93 项单元测试全部通过，使用 **DeepSeek 官方 API** 完成真实对局，并用本地假上游压测容错能力。
>
> 配套代码在本仓库 [`llm-gateway/`](../llm-gateway/) 目录。

### 2.4 CMake 构建系统

| 序号 | 笔记标题 | 类型 | 内容概要 | 链接 |
|---|---|---|---|---|
| 5 | CMake 学习内容笔记 | 学习内容 | CMake 解决的三个痛点、目标（可执行文件/库）、源码外构建、PUBLIC/PRIVATE 传递依赖、命令清单与理解、配置期/编译期/链接期错误分辨、两个 CMakeLists 的分工 | [《CMake学习内容笔记》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/onlt3g6pviouww59?singleDoc#) |
| 6 | CMake 实践任务笔记 | 实践任务 | 单位转换器项目（严格目录结构）、unitlib 库设计与六个换算函数、两个 CMakeLists 逐段讲解、`cmake ..`+`make` 四步证据、6 组换算验证、`find_package`/`install` 验证、8 条踩坑汇总 | [《CMake实践任务笔记》](https://www.yuque.com/yuwenling-mwwvy/xopzgx/ckpfnfs0gsgi98lg?singleDoc#) |

> **说明**：两篇笔记分别对应任务"学习内容"与"实践任务"的要求。配套代码在本仓库 [`UnitConverter/`](../UnitConverter/) 目录，包含根目录与 `unitlib/` 下**两个** `CMakeLists.txt`，用 CMake 构建静态库 `libunitlib.a` 与可执行文件 `unitconv`。
---

## 三、相关仓库

| 仓库 | 说明 | 链接 |
|---|---|---|
| HelloCV | 本仓库：培训任务提交仓库，含 README、笔记索引，以及 CMake 单位转换器 [`UnitConverter/`](../UnitConverter/) 与 LLM 网关 [`llm-gateway/`](../llm-gateway/) 的关键代码 | https://github.com/SuYouChiTa/HelloCV |
| git_training | Git 实践任务：C++ 四则运算计算器开发（Gitee 仓库，含加减法/乘除法分支开发与合并记录） | https://gitee.com/yuwen-ling/git_training |

---

## 四、备注

- 笔记中的命令均在实际环境（VMware + Ubuntu 26.04.1 LTS + ROS 2 `lyrical`；Windows Git Bash + Gitee 远程仓库）中执行并验证；
- 若某个链接无法访问，可能是语雀的公开权限设置问题，请通过 Issues 反馈；
- CMake 实践任务在 Ubuntu（GCC 15.2.0 + CMake 4.2.3）与 Windows（MinGW g++ + `-G "MinGW Makefiles"`）双环境下构建验证；
- 引用网络资料之处已在笔记中标注来源。
