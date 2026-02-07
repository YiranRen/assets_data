# Asset Monitor

**全球资产数据监控与展示** — 统一采集、监控并展示全球多类资产价格与指标，支持终端看板与后续告警、Web 看板等扩展。

> 📋 **产品范围**：资产类别与标的以 [PRD.md](PRD.md) 为准（美股七姐妹+VOO、A股合并展示、日股五大商社+日经指数等）。

---

## 资产类别及获取方式

项目覆盖以下资产类别，每种类别通过对应数据源/接口获取行情与指标。

| 资产类别 | 获取方式 | 数据源/接口 | 说明 |
|----------|----------|-------------|------|
| 📈 **美股** | HTTP API | Yahoo Finance (yfinance) | 美股七姐妹 + VOO；实时/盘后延迟约 15 分钟 |
| 🇨🇳 **A股** | HTTP API | 腾讯财经（主）、网易财经（备）、AKShare（备） | 沪深 A 股、主要指数（合并展示）；多源自动切换 |
| 🇯🇵 **日股** | HTTP API | Yahoo Finance (yfinance) | 五大商社 + 日经指数 |
| 🪙 **加密货币** | 交易所 API | CCXT（Binance、OKX、Coinbase 等 100+ 交易所） | 现货/合约行情，可选 WebSocket |
| 💰 **贵金属** | 交易所 + ETF | Binance 永续合约（黄金/白银）、yfinance ETF（铂金等） | 以 XAUUSDT、XAGUSDT、PPLT 等为主 |
| 💱 **外汇** | HTTP API | yfinance（以 CNY 为基准） | 主要货币对兑人民币 |
| 📊 **宏观经济** | HTTP API | yfinance（CBOE 收益率指数） | 2Y/10Y/30Y 美债收益率等 |
| 🦙 **DeFi** | HTTP API | DefiLlama API | 协议 TVL、APY、多链数据 |

**获取方式小结：**

- **HTTP API**：通过 REST 请求拉取最新价、涨跌幅等，多数为免费、有频率限制。
- **交易所 API**：通过 CCXT 或直连交易所获取 Crypto/贵金属永续等实时行情。
- **多数据源**：A股、贵金属等支持主/备源自动切换，提高可用性。

---

## ✨ 功能特性

### 核心功能

- ✅ **全资产类别覆盖** - 8大资产类别，覆盖全球主要市场
- ✅ **多数据源接入** - yfinance, CCXT, 腾讯财经、网易财经、AKShare、Binance、DefiLlama等
- ✅ **统一数据格式** - 所有资产转换为标准化格式
- ✅ **智能数据源切换** - 自动切换备用数据源，提高可靠性
- ✅ **中文名称显示** - 所有资产显示直观的中文名称
- ✅ **完整涨跌幅数据** - 24h和7天涨跌幅，颜色标注涨跌
- ✅ **美观展示** - Rich库提供的统一格式终端界面
- ✅ **可扩展架构** - 插件化采集器，易于扩展

## 🚀 快速开始

> 💡 **协作文档**：首次参与开发前请阅读 [CLAUDE.md](CLAUDE.md)，了解项目架构、代码规范和重要约定。

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装核心依赖
pip install pyyaml yfinance aiohttp pandas rich

# （可选）加密货币和贵金属支持
pip install ccxt akshare
```

### 2. 运行数据采集

```bash
# 查看统一格式数据看板（推荐）
python collect_unified.py

# 测试所有数据源
python test_all_sources.py
```

### 3. 启动 Web 看板

在项目根目录执行（需先执行一次采集以有数据）：

```bash
python3 -m uvicorn web.main:app --host 0.0.0.0 --port 8765
```

或：`chmod +x run_web.sh && ./run_web.sh`

浏览器访问：**http://127.0.0.1:8765** 或 **http://localhost:8765**。若本机访问不通，检查是否在项目根目录启动、8765 端口是否被占用（`lsof -i :8765`）。

### 4. 数据展示示例

运行 `collect_unified.py` 后可以看到统一格式的数据：

```
╭──────────────────────────────────────────────╮
│ 🚀 Asset Monitor - 全球资产监控看板          │
│ 更新时间: 2026-01-29 09:36:21 UTC           │
╰──────────────────────────────────────────────╯

┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ 资产类别 ┃ 代码     ┃ 名称            ┃ 价格   ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 美股     │ AAPL     │ 苹果公司        │ $256.44│
│ 美股     │ TSLA     │ 特斯拉          │ $431.24│
│ A股股票  │ 600519   │ 贵州茅台        │ ¥1334.39│
│ 日股商社 │ 8058.T   │ 三菱商事        │ ¥4053.00│
│ 贵金属   │ 黄金     │ Binance         │ $5522.85│
└──────────┴──────────┴─────────────────┴────────┘
```

## 📊 支持的数据源（详情）

以下为各资产类别对应的数据源说明，与上文「资产类别及获取方式」一一对应。

### 美股 (US Stocks)
- **数据源**: Yahoo Finance (yfinance)
- **覆盖**: 美股七姐妹（AAPL/MSFT/GOOGL/AMZN/NVDA/META/TSLA）+ VOO + QQQ
- **延迟**: 实时（收盘后15分钟）
- **费用**: 免费
- **支持涨跌幅**: ✅ 24h + 7天

### A股 (China Stocks)
- **数据源**: 腾讯财经（优先）、网易财经（备选）、AKShare（最后备选）
- **覆盖**: 沪深A股、主要指数
- **延迟**: 实时
- **费用**: 免费
- **支持涨跌幅**: ✅ 24h（7天需要历史存储）

### 日股 (Japan Stocks)
- **数据源**: Yahoo Finance (yfinance)
- **覆盖**: 五大商社 + 日经指数
- **延迟**: 实时
- **费用**: 免费
- **支持涨跌幅**: ✅ 24h + 7天

### 贵金属 (Precious Metals)
- **数据源**: Binance永续合约（黄金、白银优先）、yfinance ETF（铂金等）
- **覆盖**: 黄金(XAUUSDT)、白银(XAGUSDT)、铂金(PPLT)
- **延迟**: 实时
- **费用**: 免费
- **支持涨跌幅**: ✅ 24h + 7天

### 外汇 (Forex)
- **数据源**: yfinance
- **覆盖**: 主要货币对（对人民币CNY基准）
- **延迟**: 实时
- **费用**: 免费
- **支持涨跌幅**: ✅ 24h + 7天

### 宏观经济 (Macro Economic)
- **数据源**: yfinance CBOE收益率指数
- **覆盖**: 2年期、10年期、30年期美债收益率
- **延迟**: 实时
- **费用**: 免费
- **支持涨跌幅**: ✅ 24h + 7天

### 加密货币 (Crypto)
- **数据源**: CCXT
- **覆盖**: 100+交易所（Binance, OKX, Coinbase等）
- **延迟**: 实时WebSocket
- **费用**: 免费（有API限制）

### DeFi
- **数据源**: DefiLlama
- **覆盖**: 协议TVL、APY、多链数据
- **延迟**: 5分钟
- **费用**: 免费

## 📁 项目结构

```
asset-monitor/
├── config/                    # 配置文件
│   ├── config.yaml           # 主配置（包含所有数据源）
│   └── config.example.yaml   # 配置示例
│
├── src/                       # 源代码（核心）
│   ├── collectors/           # 数据采集器
│   │   ├── base.py           # 基础采集器抽象类
│   │   ├── factory.py        # 采集器工厂
│   │   ├── crypto/          # 加密货币采集器 (CCXT)
│   │   ├── stocks/          # 股票采集器
│   │   │   ├── yfinance_collector.py    # 美股
│   │   │   ├── akshare_collector.py     # A股
│   │   │   └── japan_collector.py       # 日股
│   │   ├── commodities/     # 贵金属采集器
│   │   ├── forex/           # 外汇采集器
│   │   ├── macro/           # 宏观数据采集器
│   │   └── defi/            # DeFi采集器
│   │
│   ├── processors/          # 数据处理 (标准化、验证)
│   ├── storage/             # 存储 (内存、TimescaleDB)
│   ├── utils/               # 工具类
│   └── main.py              # 主程序入口
│
├── tests/                     # 测试文件
│   ├── unit/                # 单元测试
│   └── integration/         # 集成测试
│
├── data/                      # 数据目录
├── logs/                      # 日志目录
├── collect_unified.py         # 统一格式数据采集+展示 ⭐
├── test_all_sources.py        # 综合测试脚本
├── requirements.txt           # Python依赖
├── CLAUDE.md                  # 项目协作文档
└── README.md                  # 项目说明
```

## 🧪 测试结果

### 数据采集测试（v0.2.0 - 2026-01-29）

| 类别 | 成功 | 失败 | 详情 |
|-----|------|------|------|
| 美股 | ✅ 5 | 0 | AAPL, TSLA, NVDA, SPY, QQQ |
| A股股票 | ✅ 4 | 0 | 平安银行、招商银行、贵州茅台、比亚迪 |
| A股指数 | ✅ 3 | 0 | 上证50、沪深300、深证成指 |
| 日股商社 | ✅ 5 | 0 | 三菱、三井、住友、伊藤忠、丸红 |
| 日股指数 | ✅ 1 | 0 | 日经225 |
| 贵金属 | ✅ 3 | 0 | 黄金(Binance)、白银(Binance)、铂金(ETF) |
| 外汇 | ✅ 5 | 0 | 美元、欧元、英镑、日元、港币 |
| 宏观 | ✅ 2 | 0 | 2年期、30年期美债收益率 |
| 加密货币 | - | - | 需安装ccxt |
| DeFi | - | 1 | SSL证书问题（macOS） |
| **总计** | **28** | **1** | **成功采集率: 96.6%** |

## 📋 版本历史

### v0.2.0 (2026-01-29) - 数据采集层完成

**新增功能：**
- ✅ 新增日股支持（五大商社 + 日经225）
- ✅ 统一展示格式（代码、名称、价格、单位、24h涨跌、7天涨跌）
- ✅ 所有资产中文名称映射
- ✅ 多数据源自动切换（A股、贵金属）
- ✅ 完整涨跌幅数据（24h + 7天）
- ✅ 美债收益率数据修复（使用CBOE指数）

**技术优化：**
- ✅ A股多数据源支持（腾讯、网易、AKShare）
- ✅ 贵金属Binance永续合约优先
- ✅ 外汇以CNY为基准货币
- ✅ A股股票和指数合并展示
- ✅ 涨跌幅颜色标注（绿色上涨、红色下跌）

**支持资产：**
- 美股：5个（含中文名称）
- A股：7个（4股票+3指数）
- 日股：6个（5商社+1指数）
- 贵金属：3个
- 外汇：5个
- 宏观：2个
- **总计：28个资产数据点**

### v0.1.0 (2026-01-29) - 初始版本

**基础功能：**
- ✅ 基础数据采集器框架
- ✅ CCXT加密货币采集
- ✅ yfinance股票采集
- ✅ A股、贵金属、外汇、宏观数据采集
- ✅ 统一数据格式
- ✅ Rich库美化展示

## 🔧 配置说明

### 运行统一格式看板

```bash
# 统一格式（推荐）- 包含所有资产、24h和7天涨跌幅
python collect_unified.py
```

### 添加新的美股

编辑 `collect_unified.py`：

```python
# 在美股部分添加
for symbol in ["AAPL", "TSLA", "NVDA", "SPY", "QQQ", "YOUR_SYMBOL"]:
    # 添加到映射
    us_stock_names["YOUR_SYMBOL"] = "中文名称"
```

### 添加新的A股

```python
# 在A股部分添加
for code in ["000001", "600036", "YOUR_CODE"]:
    # 添加中文名称映射到 akshare_collector.py
```

### 添加新的日股商社

```python
# 在日股部分添加
trading_companies = ["8058.T", "8031.T", "YOUR_CODE.T"]
```

## 🛠️ 开发

### 运行测试

```bash
# 测试所有数据源
python test_all_sources.py

# 测试特定功能
python test_treasury_yield.py  # 测试美债收益率
python test_data_sources.py    # 测试涨跌幅数据
```

### 代码规范

- PEP 8代码风格
- 异步IO优先（async/await）
- 完整的类型注解
- 详细的错误处理
- 中文注释和文档

## 🗺️ 路线图

### 第一阶段：数据采集 ✅ 已完成
- [x] 基础数据采集器框架
- [x] 美股数据采集（yfinance）
- [x] A股数据采集（多数据源）
- [x] 日股数据采集
- [x] 贵金属数据采集（Binance + ETF）
- [x] 外汇数据采集（CNY基准）
- [x] 宏观数据采集（美债收益率）
- [x] 统一展示格式
- [x] 完整涨跌幅数据（24h + 7天）

### 第二阶段：数据处理与存储（待开发）
- [ ] 本地数据存储（SQLite/JSON）
- [ ] 7天涨跌幅计算（A股）
- [ ] 数据清洗和验证
- [ ] 技术指标计算（MA、RSI、MACD）
- [ ] 数据聚合和统计

### 第三阶段：告警系统（待开发）
- [ ] 告警规则引擎
- [ ] Lark Bot通知
- [ ] Telegram Bot通知
- [ ] 邮件通知
- [ ] 告警聚合和去重

### 第四阶段：高级功能（待开发）
- [ ] WebSocket实时推送
- [ ] Web Dashboard（FastAPI + Vue）
- [ ] 回测系统
- [ ] 策略分析
- [ ] 移动端支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址：[GitHub](https://github.com/yourusername/asset-monitor)
- 问题反馈：[Issues](https://github.com/yourusername/asset-monitor/issues)
