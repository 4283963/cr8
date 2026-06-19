import sys
from datetime import datetime, timedelta
import random

sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app import models
from app.crud import spray_strategy as strategy_crud
from app.crud import nozzle_status as nozzle_crud
from app.crud import nutrient_solution as nutrient_crud
from app.crud import system_alert as alert_crud
from app.schemas.spray_strategy import SprayStrategyCreate
from app.schemas.nozzle_status import NozzleStatusCreate
from app.schemas.nutrient_solution import NutrientSolutionCreate
from app.schemas.system_alert import SystemAlertCreate


NOZZLE_IDS = [f"N{i:03d}" for i in range(1, 9)]


def seed_strategies(db):
    strategies = [
        SprayStrategyCreate(
            name="常规生长模式",
            description="白天每5分钟喷30秒，适用于一般生长期",
            interval_seconds=300,
            duration_seconds=30,
            start_time="06:00",
            end_time="22:00",
            is_active=True,
            nozzle_ids=",".join(NOZZLE_IDS[:4]),
        ),
        SprayStrategyCreate(
            name="夜间保湿模式",
            description="夜间每30分钟喷10秒，保持根系湿度",
            interval_seconds=1800,
            duration_seconds=10,
            start_time="22:00",
            end_time="06:00",
            is_active=True,
            nozzle_ids=",".join(NOZZLE_IDS[:4]),
        ),
        SprayStrategyCreate(
            name="幼苗模式",
            description="每2分钟喷15秒，适合幼苗期高湿度需求",
            interval_seconds=120,
            duration_seconds=15,
            start_time="06:00",
            end_time="20:00",
            is_active=False,
            nozzle_ids=",".join(NOZZLE_IDS[4:]),
        ),
    ]
    for s in strategies:
        strategy_crud.create_strategy(db, s)
    print(f"✓ 已创建 {len(strategies)} 条喷雾策略")


def seed_nozzle_statuses(db):
    now = datetime.utcnow()
    count = 0
    blocked_nozzle = "N003"

    nozzle_rest_pressure = {
        "N001": 0.35, "N002": 0.32, "N003": 0.36, "N004": 0.34,
        "N005": 0.33, "N006": 0.37, "N007": 0.31, "N008": 0.35,
    }

    latest_spraying = {"N001", "N003", "N004", "N005", "N008"}

    for i in range(60):
        recorded_at = now - timedelta(minutes=i)
        for nozzle_id in NOZZLE_IDS:
            rest_p = nozzle_rest_pressure[nozzle_id]

            if i <= 2:
                is_spraying = nozzle_id in latest_spraying
            else:
                is_spraying = random.random() < 0.3

            if nozzle_id == blocked_nozzle and i <= 10:
                is_spraying = True
                flow_rate = round(random.uniform(0.05, 0.15), 2)
                pressure = rest_p + round(random.uniform(0.02, 0.06), 3)
                is_blocked = False
                block_score = 0.0
            else:
                flow_rate = round(random.uniform(1.5, 2.8) if is_spraying else 0, 2)
                if is_spraying:
                    pressure = rest_p - round(random.uniform(0.12, 0.20), 3)
                else:
                    pressure = rest_p + round(random.uniform(-0.02, 0.02), 3)
                is_blocked = False
                block_score = 0.0

            status = NozzleStatusCreate(
                nozzle_id=nozzle_id,
                is_spraying=is_spraying,
                flow_rate=flow_rate,
                pressure=round(pressure, 3),
                is_suspected_blocked=is_blocked,
                blockage_score=block_score,
                strategy_id=random.choice([1, 2, 3, None]),
                recorded_at=recorded_at,
            )
            nozzle_crud.create_nozzle_status(db, status)
            count += 1
    print(f"✓ 已创建 {count} 条喷头状态记录（N003 模拟堵塞场景）")


def seed_demo_alerts(db):
    alerts = [
        SystemAlertCreate(
            alert_type="system",
            severity="info",
            title="系统启动完成",
            message="气雾栽培控制系统已启动，所有模块运行正常。喷头堵塞自动检测已启用。",
            related_nozzle_id=None,
            is_resolved=True,
        ),
    ]
    for alert in alerts:
        alert_crud.create_alert(db, alert)
    print(f"✓ 已创建 {len(alerts)} 条系统通知")


def seed_nutrient_records(db):
    now = datetime.utcnow()
    count = 0
    for i in range(48):
        recorded_at = now - timedelta(minutes=i * 30)
        record = NutrientSolutionCreate(
            volume_liters=round(random.uniform(80, 200), 1),
            ec_value=round(random.uniform(1.2, 2.8), 2),
            ph_value=round(random.uniform(5.5, 6.8), 2),
            temperature=round(random.uniform(18, 26), 1),
            recorded_at=recorded_at,
        )
        nutrient_crud.create_nutrient_record(db, record)
        count += 1
    print(f"✓ 已创建 {count} 条营养液记录")


def main():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("开始初始化演示数据...")
        seed_strategies(db)
        seed_nozzle_statuses(db)
        seed_nutrient_records(db)
        seed_demo_alerts(db)
        print("\n✓ 数据初始化完成！")
    finally:
        db.close()


if __name__ == "__main__":
    main()
