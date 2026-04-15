# InStock 股票分析系统

InStock股票分析系统是一个基于 FastAPI 的股票量化分析平台，提供股票数据抓取、技术指标计算、K线形态识别、策略选股等功能。采用三层架构设计，纯后端 REST API 服务，使用 MOOTDX（通达信数据接口）作为数据源。

## 技术栈

| 类别 | 技术 |
|------|------|
| Web框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 技术指标 | pandas-ta (纯Python) |
| 数据处理 | Pandas, NumPy |
| HTTP客户端 | httpx (支持异步) |
| 数据源 | MOOTDX (通达信数据接口) |
| 日志 | loguru (支持IDE跳转) |
| 定时任务 | APScheduler |

## 项目结构

```
instock-app/
├── calculator/          # 计算器层
│   ├── indicator_calculator.py    # 技术指标计算
│   └── pattern_recognizer.py      # K线形态识别
├── controller/          # 控制器层 (API接口)
│   ├── stock_controller.py        # 股票数据接口
│   ├── indicator_controller.py    # 技术指标接口
│   ├── strategy_controller.py     # 策略选股接口
│   └── backtest_controller.py     # 回测接口
├── crawler/             # 爬虫层
│   ├── tdx_fetcher.py             # MOOTDX数据获取
│   ├── trade_date_crawler.py      # 交易日历
│   └── base_crawler.py            # 爬虫基类
├── dao/                 # 数据访问层
├── entity/              # 实体类
├── service/             # 服务层
│   ├── stock_service.py           # 股票服务
│   ├── index_service.py           # 指数服务
│   ├── financial_service.py       # 财务数据服务
│   ├── indicator_service.py       # 指标计算服务
│   ├── pattern_service.py         # 形态识别服务
│   └── strategy_service.py        # 策略选股服务
├── scheduler/           # 定时任务
├── data/                # SQLite数据库目录
├── config.py            # 配置文件
├── database.py          # 数据库连接
└── main.py              # 应用入口
```

## 功能特性

### 1. 技术指标计算

支持 30+ 种技术指标：

- 趋势指标：MA、EMA、MACD、BOLL (使用 pandas-ta 计算)
- 动量指标：RSI、KDJ、CCI、WR
- 波动指标：ATR、TR
- 成交量指标：OBV、MFI、VOL_MA
- 其他：TRIX、ROC 等

### 2. K线形态识别

支持 17 种 K 线形态识别 (纯Python实现)：

- 反转形态：锤子线、倒锤子线、吞没形态、启明星、黄昏星
- 持续形态：三白兵、三只乌鸦
- 十字星类：十字星、蜻蜓十字星、墓碑十字星
- 其他：流星线、上吊线、乌云盖顶、刺透形态等

### 3. 策略选股

内置多种选股策略：

- 放量上涨
- 突破平台
- 低ATR
- 海龟交易
- 高紧旗
- 停机坪
- 持续上涨

### 4. 数据抓取 (MOOTDX)

- 股票实时行情（含五档买卖盘）
- 股票历史K线（日线/周线/月线）
- 股票分时数据（1/5/15/30/60分钟）
- 股票列表（A股全量，过滤北交所）
- 指数实时行情（上证指数、深证成指、创业板指等9只主要指数）
- 财务数据（300+字段，含每股指标、盈利能力、成长能力、资产负债、现金流等）
- 交易日历

### 5. 指数行情

支持9只主要指数实时行情：
- 上证指数 (000001)
- 上证50 (000016)
- 沪深300 (000300)
- 中证500 (000905)
- 中证1000 (000852)
- 深证成指 (399001)
- 创业板指 (399006)
- 中小板指 (399005)

### 6. 财务数据

精简核心财务指标（26个字段）：
- 每股指标：EPS、扣非EPS、每股净资产、每股现金流
- 盈利能力：ROE、销售净利率、销售毛利率
- 成长能力：营收增长率、净利润增长率
- 资产负债：资产负债率、流动比率、速动比率
- 核心财务：营收、净利润、总资产、净资产
- 现金流：经营/投资/筹资现金流
- 股本数据：总股本、流通A股

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
cd app
python -m app.main
```

服务启动后会自动：
1. 创建数据库目录 `data/`
2. 创建 SQLite 数据库文件
3. 创建所有数据表
4. 若是交易日且无数据，自动获取当日股票数据

### 访问 API 文档

- Swagger UI: http://localhost:9988/docs
- ReDoc: http://localhost:9988/redoc

## 文档索引

| 文档 | 说明 |
|------|------|
| [USER_GUIDE.md](USER_GUIDE.md) | 用户指南（安装、配置、使用、注意事项） |
| [FAQ.md](FAQ.md) | 常见问题解答 |
| [interface.md](interface.md) | API接口详细文档 |

## API 接口文档

详细的API接口文档请查看 [interface.md](interface.md)。

### 接口概览

| 接口模块 | 路径 | 说明 |
|----------|------|------|
| 股票数据 | `/api/stocks` | 股票行情、历史数据、分时数据 |
| 指数行情 | `/api/index` | 上证、深证、创业板等主要指数 |
| 财务数据 | `/api/financial` | 股票财务报表、历史财务数据 |
| 技术指标 | `/api/indicators` | MACD、KDJ、RSI等技术指标计算 |
| K线形态 | `/api/patterns` | 锤头、吞没、早晨之星等形态识别 |
| 策略选股 | `/api/strategy` | 放量上涨、突破平台等选股策略 |
| 回测 | `/api/backtest` | 策略历史回测、收益分析 |
| 关注股票 | `/api/attention` | 用户自选股管理（添加/删除/查询） |
| 历史缓存 | `/api/hist` | K线数据本地缓存（减少请求频率） |

### 通用响应格式

```json
{
    "code": 0,
    "message": "success",
    "data": {}
}
```

---

## 配置说明

配置文件：`app/config.py`

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务地址 |
| `PORT` | 9988 | 服务端口 |
| `DB_FILE` | data/instock.db | 数据库文件路径 |
| `SCHEDULER_ENABLED` | True | 是否启用定时任务 |
| `PROXY_ENABLED` | False | 是否启用代理 |

## 定时任务

系统内置以下定时任务：

| 任务 | 时间 | 说明 |
|------|------|------|
| 每日数据抓取 | 15:30 | 抓取当日股票数据 |
| 指标计算 | 16:00 | 计算技术指标 |
| 策略选股 | 16:30 | 运行选股策略 |

## 数据库

使用 SQLite 数据库，数据文件位于 `app/data/instock.db`。

主要数据表：
- `cn_stock_spot` - 股票实时行情（含五档买卖盘）
- `cn_stock_index_spot` - 指数实时行情
- `cn_stock_financial` - 股票财务数据（核心指标）
- `cn_stock_indicator` - 技术指标
- `cn_stock_pattern` - K线形态
- `cn_stock_strategy_*` - 策略选股结果

## 开发说明

### 三层架构

```
Controller (API接口)
    ↓
Service (业务逻辑)
    ↓
DAO (数据访问)
    ↓
Entity (数据实体)
```

### 添加新功能

1. 在 `entity/` 创建实体类
2. 在 `dao/` 创建数据访问类
3. 在 `service/` 创建业务服务类
4. 在 `controller/` 创建 API 接口
5. 在 `main.py` 注册路由

## 注意事项

- 数据来源：MOOTDX（通达信数据接口）
- 本系统仅供学习研究使用
- 股市有风险，投资需谨慎

## License

MIT License