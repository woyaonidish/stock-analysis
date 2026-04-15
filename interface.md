# InStock API 接口文档

## 通用响应格式

```json
{
    "code": 0,
    "message": "success",
    "data": {}
}
```

---

## 1. 股票数据接口 (/api/stocks)

### 1.1 获取股票列表

**接口**：`GET /api/stocks/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD)，默认当天 |

**请求示例**：
```
GET /api/stocks/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "平安银行",
            "open_price": 12.10,
            "close_price": 12.34,
            "high_price": 12.50,
            "low_price": 12.05,
            "volume": 12345678,
            "amount": 152345678.90,
            "bid1": 12.33,
            "bid1_vol": 5000,
            "ask1": 12.34,
            "ask1_vol": 3000
        }
    ]
}
```

---

### 1.2 获取股票详情

**接口**：`GET /api/stocks/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
GET /api/stocks/000001?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "name": "平安银行",
        "date": "2026-04-08",
        "open_price": 12.10,
        "close_price": 12.34,
        "high_price": 12.50,
        "low_price": 12.05,
        "pre_close_price": 12.08,
        "volume": 12345678,
        "amount": 152345678.90,
        "bid1": 12.33,
        "bid1_vol": 5000,
        "ask1": 12.34,
        "ask1_vol": 3000
    }
}
```

---

### 1.3 获取股票历史数据

**接口**：`GET /api/stocks/{code}/hist`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| start_date | string | 否 | 开始日期(YYYYMMDD) |
| end_date | string | 否 | 结束日期(YYYYMMDD) |
| period | string | 否 | 周期：daily/weekly/monthly，默认daily |

**请求示例**：
```
GET /api/stocks/000001/hist?start_date=20260101&end_date=20260408&period=daily
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "date": "2026-04-08",
            "open": 12.10,
            "close": 12.34,
            "high": 12.50,
            "low": 12.05,
            "volume": 12345678,
            "amount": 152345678.90
        }
    ]
}
```

---

### 1.4 获取股票分时数据

**接口**：`GET /api/stocks/{code}/min`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| period | string | 否 | 周期：1/5/15/30/60分钟，默认5 |

**请求示例**：
```
GET /api/stocks/000001/min?period=5
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "time": "2026-04-08 09:35:00",
            "open": 12.10,
            "close": 12.15,
            "high": 12.18,
            "low": 12.08,
            "volume": 123456,
            "amount": 1498765.00
        }
    ]
}
```

---

### 1.5 搜索股票

**接口**：`GET /api/stocks/search/{keyword}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | string | 是 | 搜索关键词（代码或名称） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/stocks/search/平安
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "平安银行",
            "close_price": 12.34
        }
    ]
}
```

---

### 1.6 抓取并保存每日数据

**接口**：`POST /api/stocks/fetch`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
POST /api/stocks/fetch?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 5200
    }
}
```

---

## 2. 指数行情接口 (/api/index)

### 2.1 获取指数列表

**接口**：`GET /api/index/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD)，默认当天 |

**请求示例**：
```
GET /api/index/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "上证指数",
            "date": "2026-04-08",
            "open_price": 3250.50,
            "close_price": 3280.25,
            "high_price": 3295.00,
            "low_price": 3245.00,
            "pre_close": 3250.00,
            "change_rate": 0.93,
            "volume": 256789000,
            "amount": 3521678900
        }
    ]
}
```

---

### 2.2 获取指数详情

**接口**：`GET /api/index/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 指数代码（路径参数） |
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**支持指数**：
- 000001 - 上证指数
- 000016 - 上证50
- 000300 - 沪深300
- 000905 - 中证500
- 000852 - 中证1000
- 399001 - 深证成指
- 399005 - 中小板指
- 399006 - 创业板指

**请求示例**：
```
GET /api/index/000001?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "name": "上证指数",
        "date": "2026-04-08",
        "open_price": 3250.50,
        "close_price": 3280.25,
        "high_price": 3295.00,
        "low_price": 3245.00,
        "pre_close": 3250.00,
        "change_rate": 0.93,
        "volume": 256789000,
        "amount": 3521678900
    }
}
```

---

### 2.3 抓取并保存指数数据

**接口**：`POST /api/index/fetch`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
POST /api/index/fetch?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 8
    }
}
```

---

## 3. 财务数据接口 (/api/financial)

### 3.1 获取股票财务数据

**接口**：`GET /api/financial/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| report_date | string | 否 | 报告期(YYYY-MM-DD)，默认最新 |

**请求示例**：
```
GET /api/financial/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "report_date": "2025-12-31",
        "eps": 1.25,
        "eps_deducted": 1.18,
        "bvps": 18.50,
        "cfps": 2.30,
        "roe": 12.5,
        "roe_weighted": 13.2,
        "net_profit_margin": 25.6,
        "gross_profit_margin": 45.8,
        "revenue_growth": 8.5,
        "net_profit_growth": 12.3,
        "debt_ratio": 62.5,
        "current_ratio": 1.85,
        "quick_ratio": 1.45,
        "revenue": 45678900000,
        "net_profit": 11674500000,
        "total_assets": 589678000000,
        "net_assets": 221345000000,
        "total_shares": 19405000000
    }
}
```

---

### 3.2 获取历史财务数据

**接口**：`GET /api/financial/{code}/history`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| limit | int | 否 | 返回数量，默认8个报告期 |

**请求示例**：
```
GET /api/financial/000001/history?limit=4
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "report_date": "2025-12-31",
            "eps": 1.25,
            "roe": 12.5,
            "revenue": 45678900000,
            "net_profit": 11674500000
        }
    ]
}
```

---

### 3.3 获取最新报告期

**接口**：`GET /api/financial/latest-report-date`

**参数**：无

**请求示例**：
```
GET /api/financial/latest-report-date
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "report_date": "2025-12-31"
    }
}
```

---

### 3.4 解析财务数据文件

**接口**：`POST /api/financial/parse`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| filepath | string | 是 | 财务数据文件路径(gpcw*.zip) |

**请求示例**：
```
POST /api/financial/parse?filepath=./data/gpcw20231231.zip
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 5200
    }
}
```

**备注**：需先下载财务数据文件：
```bash
python -c "from mootdx.affair import Affair; Affair.fetch(downdir='./data', filename='gpcw20231231.zip')"
```

---

## 4. 技术指标接口 (/api/indicators)

### 4.1 获取股票指标

**接口**：`GET /api/indicators/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "date": "2026-04-08",
        "macd": 0.123,
        "macds": 0.456,
        "macdh": 0.067,
        "kdjk": 78.5,
        "kdjd": 65.2,
        "kdjj": 105.1,
        "rsi": 62.3,
        "atr": 0.35,
        "cci": 85.6
    }
}
```

---

### 4.2 获取所有股票指标

**接口**：`GET /api/indicators/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "date": "2026-04-08",
            "macd": 0.123,
            "kdjk": 78.5,
            "rsi": 62.3
        }
    ]
}
```

---

### 4.3 获取买入信号

**接口**：`GET /api/indicators/signals/buy`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/signals/buy
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {"code": "000001", "date": "2026-04-08"},
        {"code": "000002", "date": "2026-04-08"}
    ]
}
```

---

### 4.4 获取卖出信号

**接口**：`GET /api/indicators/signals/sell`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/indicators/signals/sell
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {"code": "600000", "date": "2026-04-08"}
    ]
}
```

---

### 4.5 计算并保存指标

**接口**：`POST /api/indicators/calculate/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
POST /api/indicators/calculate/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001"
    }
}
```

---

## 5. K线形态接口 (/api/patterns)

### 5.1 获取股票形态

**接口**：`GET /api/patterns/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
GET /api/patterns/000001?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "date": "2026-04-08",
        "patterns": {
            "hammer": 100,
            "engulfing_pattern": 100,
            "morning_star": 100
        }
    }
}
```

---

### 5.2 获取形态列表

**接口**：`GET /api/patterns/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
GET /api/patterns/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "date": "2026-04-08",
            "patterns": {"hammer": 100}
        }
    ]
}
```

---

### 5.3 获取买入信号

**接口**：`GET /api/patterns/signals/buy`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
GET /api/patterns/signals/buy?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "date": "2026-04-08",
            "pattern": "hammer",
            "signal": "buy"
        }
    ]
}
```

**说明**：正值(100)表示看涨形态，包括锤头、早晨之星、吞没形态等。

---

### 5.4 获取卖出信号

**接口**：`GET /api/patterns/signals/sell`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
GET /api/patterns/signals/sell?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "600000",
            "date": "2026-04-08",
            "pattern": "hanging_man",
            "signal": "sell"
        }
    ]
}
```

**说明**：负值(-100)表示看跌形态，包括上吊线、黄昏之星、乌云盖顶等。

---

### 5.5 计算并保存形态

**接口**：`POST /api/patterns/calculate/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
POST /api/patterns/calculate/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001"
    }
}
```

---

### 5.6 批量计算形态

**接口**：`POST /api/patterns/calculate-all`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD) |

**请求示例**：
```
POST /api/patterns/calculate-all?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 1250
    }
}
```

---

## 6. 策略选股接口 (/api/strategy)

### 6.1 获取策略类型列表

**接口**：`GET /api/strategy/types`

**参数**：无

**请求示例**：
```
GET /api/strategy/types
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {"type": "volume_up", "name": "放量上涨"},
        {"type": "breakthrough", "name": "突破平台"},
        {"type": "low_atr", "name": "低ATR"},
        {"type": "turtle", "name": "海龟交易"},
        {"type": "high_tight_flag", "name": "高紧旗"},
        {"type": "parking_apron", "name": "停机坪"},
        {"type": "keep_increasing", "name": "持续上涨"}
    ]
}
```

---

### 6.2 获取策略结果

**接口**：`GET /api/strategy/{strategy_type}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| strategy_type | string | 是 | 策略类型（路径参数） |
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
GET /api/strategy/volume_up?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "date": "2026-04-08",
            "strategy_type": "volume_up",
            "score": 1.0
        }
    ]
}
```

---

### 6.3 运行策略

**接口**：`POST /api/strategy/run`

**请求体**：
```json
{
    "strategy_type": "volume_up",
    "trade_date": "2026-04-08"
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| strategy_type | string | 是 | 策略类型 |
| trade_date | string | 否 | 交易日期 |

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "strategy_type": "volume_up",
        "trade_date": "2026-04-08",
        "count": 125
    }
}
```

---

### 6.4 运行所有策略

**接口**：`POST /api/strategy/run-all`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期 |

**请求示例**：
```
POST /api/strategy/run-all?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "volume_up": 125,
        "breakthrough": 45,
        "low_atr": 89,
        "turtle": 32
    }
}
```

---

## 7. 回测接口 (/api/backtest)

### 7.1 运行回测

**接口**：`POST /api/backtest/run`

**请求体**：
```json
{
    "strategy_type": "volume_up",
    "start_date": "2025-01-01",
    "end_date": "2026-04-08",
    "initial_capital": 100000.0
}
```

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| strategy_type | string | 是 | 策略类型 |
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |
| initial_capital | float | 否 | 初始资金，默认100000 |

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "strategy_type": "volume_up",
        "total_return": 15.6,
        "annual_return": 12.3,
        "max_drawdown": -8.5,
        "sharpe_ratio": 1.25,
        "win_rate": 58.5,
        "total_trades": 156
    }
}
```

---

### 7.2 运行所有策略回测

**接口**：`POST /api/backtest/run-all`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |

**请求示例**：
```
POST /api/backtest/run-all?start_date=2025-01-01&end_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "volume_up": {"total_return": 15.6, "sharpe_ratio": 1.25},
        "breakthrough": {"total_return": 12.3, "sharpe_ratio": 1.05},
        "low_atr": {"total_return": 18.9, "sharpe_ratio": 1.45}
    }
}
```

---

## 8. 关注股票接口 (/api/attention)

用户自选股管理接口，支持添加、删除、查询关注股票。

### 8.1 获取关注股票列表

**接口**：`GET /api/attention/list`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| trade_date | string | 否 | 交易日期(YYYY-MM-DD)，返回关注股票的行情信息 |

**请求示例**：
```
GET /api/attention/list?trade_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "code": "000001",
            "name": "平安银行",
            "date": "2026-04-08",
            "close_price": 12.34,
            "change_rate": 2.15,
            "volume": 12345678,
            "amount": 152345678.90
        }
    ]
}
```

---

### 8.2 获取关注股票代码

**接口**：`GET /api/attention/codes`

**参数**：无

**请求示例**：
```
GET /api/attention/codes
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": ["000001", "000002", "600000"]
}
```

---

### 8.3 检查是否关注

**接口**：`GET /api/attention/check/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |

**请求示例**：
```
GET /api/attention/check/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "is_attention": true
    }
}
```

---

### 8.4 添加关注

**接口**：`POST /api/attention/add/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |

**请求示例**：
```
POST /api/attention/add/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {"code": "000001"}
}
```

---

### 8.5 取消关注

**接口**：`DELETE /api/attention/remove/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |

**请求示例**：
```
DELETE /api/attention/remove/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {"code": "000001"}
}
```

---

### 8.6 清空关注列表

**接口**：`DELETE /api/attention/clear`

**参数**：无

**请求示例**：
```
DELETE /api/attention/clear
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {"count": 5}
}
```

---

## 9. 历史数据缓存接口 (/api/hist)

历史K线数据本地缓存接口，减少对外部数据源的请求频率。

### 9.1 获取缓存历史数据

**接口**：`GET /api/hist/cache/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| start_date | string | 否 | 开始日期(YYYY-MM-DD)，默认一年前 |
| end_date | string | 否 | 结束日期(YYYY-MM-DD)，默认当天 |

**请求示例**：
```
GET /api/hist/cache/000001?start_date=2025-01-01&end_date=2026-04-08
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": [
        {
            "date": "2026-04-08",
            "open": 12.10,
            "close": 12.34,
            "high": 12.50,
            "low": 12.05,
            "volume": 12345678,
            "amount": 152345678.90,
            "amplitude": 3.72,
            "quote_change": 2.15,
            "ups_downs": 0.26,
            "turnover": 0.85
        }
    ]
}
```

---

### 9.2 获取缓存状态

**接口**：`GET /api/hist/status/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |

**请求示例**：
```
GET /api/hist/status/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "cache_count": 365,
        "latest_date": "2026-04-08"
    }
}
```

---

### 9.3 获取并缓存历史数据

**接口**：`POST /api/hist/fetch/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |
| days | int | 否 | 获取天数，默认365 |

**请求示例**：
```
POST /api/hist/fetch/000001?days=180
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "count": 180
    }
}
```

---

### 9.4 批量获取并缓存历史数据

**接口**：`POST /api/hist/fetch-batch`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | int | 否 | 获取天数，默认365 |
| codes | string | 否 | 股票代码列表(逗号分隔)，不填则获取全市场 |

**请求示例**：
```
POST /api/hist/fetch-batch?days=180&codes=000001,000002,600000
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total_count": 540,
        "success_count": 3,
        "processed": 3
    }
}
```

**说明**：批量获取限制50只股票，避免请求过多。

---

### 9.5 清除缓存

**接口**：`DELETE /api/hist/clear/{code}`

**参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 股票代码（路径参数） |

**请求示例**：
```
DELETE /api/hist/clear/000001
```

**响应示例**：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "code": "000001",
        "count": 365
    }
}
```