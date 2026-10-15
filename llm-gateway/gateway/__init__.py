"""石头剪刀布决策网关（教学用）。

数据流::

    每一行一个 JSON 请求               每一行一个 JSON 决策
    {"time": "...", "history": [...]}  ->  {"time": "...", "option": "rock|scissor|paper"}
            │
            └─> DeepSeek 官方 API（json_object 模式）─> JSON 容错整理 ─> 合法性校验 ─> 兜底

模块划分：

* :mod:`gateway.json_guard` —— 把模型返回的任意文本整理成 JSON 对象（本练习的核心）
* :mod:`gateway.rules`      —— 决策字段的校验、规范化与兜底
* :mod:`gateway.client`     —— HTTP 转发与重试（超时、退避、空回复）
* :mod:`gateway.app`        —— 串起上面三步，保证「一行进、一行合法 JSON 出」
* :mod:`gateway.game`       —— 裁判与对战循环，用来实际玩一局
"""

__version__ = "1.0.0"
