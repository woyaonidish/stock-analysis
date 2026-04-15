# InStock 常见问题 (FAQ)

本文档收集 InStock 股票分析系统的常见问题及解决方案。

---

## 目录

- [Q1: 启动时报错 ModuleNotFoundError](#q1-启动时报错-modulenotfounderror)
- [Q2: 数据抓取返回空数据](#q2-数据抓取返回空数据)
- [Q3: 部分股票代码无法获取数据](#q3-部分股票代码无法获取数据)
- [Q4: 数据库文件在哪里](#q4-数据库文件在哪里)
- [Q5: 如何关闭定时任务](#q5-如何关闭定时任务)
- [Q6: 批次保存报错 UNIQUE constraint failed](#q6-批次保存报错-unique-constraint-failed)

---

## Q1: 启动时报错 "ModuleNotFoundError"

**原因**：依赖未完整安装

**解决**：
```bash
pip install -r requirements.txt
```

**验证安装**：
```bash
python -c "import fastapi; import mootdx; import pandas_ta; print('依赖安装成功')"
```

---

## Q2: 数据抓取返回空数据

**可能原因**：
- 当天不是交易日（周末/节假日）
- 网络无法连接通达信服务器
- 当前时间不在交易时段（9:30-15:00）

**解决**：检查网络连接，或在交易日交易时段后抓取

**检查网络**：
```bash
# 测试通达信服务器连接
ping 119.147.212.81
```

---

## Q3: 部分股票代码无法获取数据

**原因**：系统已过滤北交所股票（8xxxxx、4xxxxx），MOOTDX 不支持

**说明**：这是设计行为，只支持沪深主板、创业板、科创板

**支持的股票代码格式**：

| 市场 | 代码格式 | 示例 |
|------|----------|------|
| 上证主板 | 60xxxx | 600000、601318 |
| 上证科创板 | 68xxxx | 688001 |
| 深证主板 | 00xxxx | 000001、000002 |
| 深证创业板 | 30xxxx | 300001、300750 |

**已过滤**：北交所（8xxxxx、4xxxxx）不支持

---

## Q4: 数据库文件在哪里

**位置**：`app/data/instock.db`

**查看数据**：
```bash
# 使用 SQLite 命令行
sqlite3 app/data/instock.db

# 或使用 DB Browser for SQLite 等工具
```

**常用查询**：
```sql
-- 查看表结构
.tables

-- 查看今日股票数量
SELECT COUNT(*) FROM cn_stock_spot WHERE date = '2026-04-16';

-- 查看最新数据日期
SELECT MAX(date) FROM cn_stock_spot;
```

---

## Q5: 如何关闭定时任务

**方法**：修改配置文件

```python
# app/config/config.py
SCHEDULER_ENABLED = False
```

**说明**：
- 关闭后不会自动抓取数据
- 需手动通过 API 触发数据抓取

**手动触发**：
```bash
curl -X POST "http://localhost:9988/api/stocks/fetch"
```

---

## Q6: 批次保存报错 "UNIQUE constraint failed"

**错误信息**：
```
UNIQUE constraint failed: cn_stock_spot.date, cn_stock_spot.code
This Session's transaction has been rolled back...
```

**原因**：批次保存时遇到已存在的数据（date+code 主键重复）

**解决**：已修复，使用 upsert 策略（先删除后插入）

**说明**：
- 系统已改用 `upsert_all` 方法处理重复数据
- 同一日期的数据会先删除再插入，避免约束冲突
- 若仍遇到问题，可手动删除当日数据后重试：

```bash
# 通过API重新抓取当日数据
curl -X POST "http://localhost:9988/api/stocks/fetch"
```

---

## 更多问题

如有其他问题，请查阅：
- [USER_GUIDE.md](USER_GUIDE.md) - 用户指南
- [interface.md](interface.md) - API接口文档
- [README.md](README.md) - 项目说明