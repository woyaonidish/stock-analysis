# InStock 股票分析系统

InStock股票分析系统是一个基于 FastAPI 的股票量化分析平台，提供股票数据抓取、技术指标计算、K线形态识别、策略选股等功能。采用三层架构设计，纯后端 REST API 服务。

## 技术栈

| 类别 | 技术 |
|------|------|
| Web框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 技术指标 | pandas-ta (纯Python) |
| 数据处理 | Pandas, NumPy |
| 定时任务 | APScheduler |

## 项目结构

```
instock-app/
├── calculator/          # 计算器层
│   ├── indicator_calculator.py    # 技术指标计算
│   └── pattern_recognizer.py      # K线形态识别
├── controller/          # 控制器层 (API接口)
│   ├── stock_controller.py        # 股票数据接口
│   ├── etf_controller.py          # ETF数据接口
│   ├── fund_flow_controller.py    # 资金流向接口
│   ├── indicator_controller.py    # 技术指标接口
│   ├── strategy_controller.py     # 策略选股接口
│   └── backtest_controller.py     # 回测接口
├── crawler/             # 爬虫层
│   ├── stock_hist_crawler.py      # 股票历史数据
│   ├── stock_fund_crawler.py      # 资金流向数据
│   ├── etf_crawler.py             # ETF数据
│   └── trade_date_crawler.py      # 交易日历
├── dao/                 # 数据访问层
├── entity/              # 实体类
├── service/             # 服务层
│   ├── stock_service.py           # 股票服务
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

### 4. 数据抓取

- 股票实时行情
- 股票历史K线（日线/周线/月线/分时）
- 资金流向排名
- ETF行情数据
- 交易日历

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

### 访问 API 文档

- Swagger UI: http://localhost:9988/docs
- ReDoc: http://localhost:9988/redoc

## API 接口

### 股票数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stocks/list` | GET | 获取股票列表 |
| `/api/stocks/{code}` | GET | 获取股票详情 |
| `/api/stocks/{code}/hist` | GET | 获取历史K线 |
| `/api/stocks/{code}/min` | GET | 获取分时数据 |
| `/api/stocks/fetch` | POST | 抓取每日数据 |

### 技术指标

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/indicators/calculate` | POST | 计算技术指标 |
| `/api/indicators/{code}` | GET | 获取股票指标 |

### 策略选股

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/strategy/run` | POST | 运行选股策略 |
| `/api/strategy/results` | GET | 获取策略结果 |

## 配置说明

配置文件：`instock-app/config.py`

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务地址 |
| `PORT` | 9988 | 服务端口 |
| `DB_FILE` | data/instock.db | 数据库文件路径 |
| `SCHEDULER_ENABLED` | True | 是否启用定时任务 |

## 定时任务

系统内置以下定时任务：

| 任务 | 时间 | 说明 |
|------|------|------|
| 每日数据抓取 | 15:30 | 抓取当日股票数据 |
| 指标计算 | 16:00 | 计算技术指标 |
| 策略选股 | 16:30 | 运行选股策略 |

## 数据库

使用 SQLite 数据库，数据文件位于 `instock-app/data/instock.db`。

主要数据表：
- `cn_stock_spot` - 股票实时行情
- `cn_stock_indicators` - 技术指标
- `cn_stock_pattern` - K线形态
- `cn_stock_strategy_*` - 策略选股结果
- `cn_etf_spot` - ETF行情
- `cn_stock_fund_flow` - 资金流向

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

- 数据来源：东方财富网
- 本系统仅供学习研究使用
- 股市有风险，投资需谨慎

## License

MIT License