# 气雾栽培温室控制系统

植物根系气雾栽培自动化管理系统，包含定时喷雾策略管理、喷头状态监控、营养液数据采集等功能。

## 技术栈

**后端**
- Python 3.10+
- FastAPI 0.115
- SQLAlchemy 2.0
- Pydantic 2.9
- SQLite（默认，可切换 PostgreSQL/MySQL）

**前端**
- Vue 3 (Composition API)
- Vite 5
- Pinia (状态管理)
- Vue Router 4
- ECharts 5 (数据可视化)
- Axios (HTTP 客户端)

## 项目结构

```
cr8/
├── backend/                    # 后端 FastAPI 项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   │   ├── base.py
│   │   │   ├── spray_strategy.py
│   │   │   ├── nozzle_status.py
│   │   │   └── nutrient_solution.py
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── spray_strategy.py
│   │   │   ├── nozzle_status.py
│   │   │   └── nutrient_solution.py
│   │   ├── crud/              # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── spray_strategy.py
│   │   │   ├── nozzle_status.py
│   │   │   └── nutrient_solution.py
│   │   └── routers/           # API 路由
│   │       ├── __init__.py
│   │       ├── spray_strategy.py
│   │       ├── nozzle_status.py
│   │       └── nutrient_solution.py
│   ├── seed_data.py           # 演示数据初始化脚本
│   ├── requirements.txt
│   └── aeroponics.db          # 运行后自动生成
│
└── frontend/                   # 前端 Vue 项目
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/
        │   └── index.js       # 路由配置
        ├── api/
        │   └── index.js       # API 服务层
        ├── stores/            # Pinia 状态管理
        │   ├── strategy.js
        │   ├── nozzle.js
        │   └── nutrient.js
        ├── styles/
        │   └── global.css
        ├── components/
        │   └── StrategyModal.vue
        └── views/             # 页面视图
            ├── Dashboard.vue       # 状态监控页
            └── Strategies.vue      # 策略编排页
```

## 快速开始

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化演示数据（可选，会重置数据库）
python seed_data.py

# 启动服务（默认端口 8000）
uvicorn app.main:app --reload
```

后端启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 5173）
npm run dev
```

前端启动后访问 http://localhost:5173

## 功能说明

### 🌱 喷雾策略管理

- **策略列表**: 卡片式展示所有喷雾策略，显示间隔、时长、时段等信息
- **新建策略**: 配置喷雾间隔秒数、持续秒数、生效时间段、关联喷头
- **编辑/删除**: 灵活修改策略参数或删除策略
- **启停切换**: 一键启用或停用策略
- **时段控制**: 支持只在特定时间段（如 06:00-22:00）内执行

### 📊 状态监控仪表盘

**营养液数据**
- 当前存量（升）
- EC 电导率值（mS/cm）
- pH 值
- 液体温度
- 近 24 小时趋势折线图

**喷头状态**
- 喷头总数、喷雾中/空闲数量统计
- 工作状态环形饼图
- 各喷头实时流量柱状图
- 喷头状态列表（含流量、压力）
- 30 秒自动刷新数据

## API 接口

所有接口前缀: `/api/v1`

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 喷雾策略 | GET | `/strategies` | 获取策略列表 |
| | GET | `/strategies/active` | 获取当前生效策略 |
| | GET | `/strategies/{id}` | 获取单个策略 |
| | POST | `/strategies` | 创建策略 |
| | PUT | `/strategies/{id}` | 更新策略 |
| | PATCH | `/strategies/{id}/toggle` | 启停策略 |
| | DELETE | `/strategies/{id}` | 删除策略 |
| 喷头状态 | GET | `/nozzles` | 获取状态记录列表 |
| | GET | `/nozzles/latest` | 获取各喷头最新状态 |
| | GET | `/nozzles/stats` | 获取喷头统计数据 |
| | GET | `/nozzles/{nozzle_id}/latest` | 获取单喷头最新状态 |
| | POST | `/nozzles` | 上报喷头状态 |
| 营养液 | GET | `/nutrient` | 获取营养液记录列表 |
| | GET | `/nutrient/latest` | 获取最新营养液数据 |
| | POST | `/nutrient` | 上报营养液数据 |
