import sys
from datetime import datetime, timedelta
import random

sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app import models
from app.crud import spray_strategy as strategy_crud
from app.crud import nozzle_status as nozzle_crud
from app.crud import nutrient_solution as nutrient_crud
from app.schemas.spray_strategy import SprayStrategyCreate
from app.schemas.nozzle_status import NozzleStatusCreate
from app.schemas.nutrient_solution import NutrientSolutionCreate


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
    for i in range(60):
        recorded_at = now - timedelta(minutes=i)
        for nozzle_id in NOZZLE_IDS:
            is_spraying = random.random() < 0.3
            status = NozzleStatusCreate(
                nozzle_id=nozzle_id,
                is_spraying=is_spraying,
                flow_rate=round(random.uniform(0, 2.5) if is_spraying else 0, 2),
                pressure=round(random.uniform(0.2, 0.5), 2),
                strategy_id=random.choice([1, 2, 3, None]),
                recorded_at=recorded_at,
            )
            nozzle_crud.create_nozzle_status(db, status)
            count += 1
    print(f"✓ 已创建 {count} 条喷头状态记录")


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
        print("\n✓ 数据初始化完成！")
    finally:
        db.close()


if __name__ == "__main__":
    main()
