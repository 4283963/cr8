import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..crud import nozzle_status as nozzle_crud
from ..crud import system_alert as alert_crud
from ..models.nozzle_status import NozzleStatus

logger = logging.getLogger(__name__)

PRESSURE_DROP_THRESHOLD = 0.03
CONSECUTIVE_FAILURES_THRESHOLD = 2
CHECK_INTERVAL_SECONDS = 10

NOZZLE_IDS = [f"N{i:03d}" for i in range(1, 9)]


class SprayState:
    def __init__(self):
        self.last_status: Dict[str, dict] = {}
        self.resting_pressure: Dict[str, float] = {}
        self.consecutive_failures: Dict[str, int] = defaultdict(int)
        self.spraying_since: Dict[str, datetime] = {}
        self.currently_spraying: Dict[str, bool] = {}

    def update_last_status(self, status: NozzleStatus):
        self.last_status[status.nozzle_id] = {
            "id": status.id,
            "nozzle_id": status.nozzle_id,
            "is_spraying": status.is_spraying,
            "pressure": status.pressure,
            "flow_rate": status.flow_rate,
            "is_suspected_blocked": status.is_suspected_blocked,
            "blockage_score": status.blockage_score,
        }


spray_state = SprayState()


def analyze_pressure_behavior(
    nozzle_id: str,
    current_pressure: float,
    baseline_pressure: float,
    is_spraying: bool,
) -> tuple[bool, float]:
    """
    分析喷头喷雾时的压力行为。

    研判逻辑：
    - 正常喷雾时，管道压力应该下降（因为水从喷头喷出）
    - 如果压力没有下降甚至上升，说明喷头可能堵塞
    - 压力下降幅度小于 PRESSURE_DROP_THRESHOLD (0.03 MPa) 视为异常
    """
    if not is_spraying or baseline_pressure is None:
        return False, 0.0

    pressure_diff = current_pressure - baseline_pressure

    if pressure_diff >= -PRESSURE_DROP_THRESHOLD:
        if pressure_diff >= 0:
            score = min(1.0, 0.6 + abs(pressure_diff) * 2)
        else:
            score = min(0.7, 0.4 + abs(pressure_diff) * 3)
        return True, score

    return False, 0.0


def initialize_resting_pressures(db: Session):
    """
    初始化各喷头的静止压力基线（从数据库中查询最近的非喷雾状态记录）。
    """
    for nozzle_id in NOZZLE_IDS:
        recent, _ = nozzle_crud.get_nozzle_statuses(
            db, nozzle_id=nozzle_id, limit=20
        )
        for record in recent:
            if not record.is_spraying and record.pressure is not None:
                spray_state.resting_pressure[nozzle_id] = record.pressure
                logger.info(
                    f"[{nozzle_id}] 初始静止压力基线: {record.pressure:.3f} MPa"
                )
                break


def check_nozzle_blockage(db: Session):
    """
    检查所有喷头是否存在堵塞嫌疑。

    工作流程：
    1. 获取所有喷头的最新状态
    2. 检测喷雾开始事件（is_spraying 从 False -> True），记录此时压力
    3. 喷雾期间持续监测压力
    4. 如果压力未按预期下降，增加故障计数
    5. 连续多次异常则标记为堵塞，并创建系统告警
    """
    logger.info("开始执行喷头堵塞检测...")
    latest_statuses = nozzle_crud.get_all_latest_statuses(db)
    logger.info(f"检测到 {len(latest_statuses)} 个喷头的最新状态")

    for status in latest_statuses:
        nozzle_id = status.nozzle_id
        current_pressure = status.pressure
        is_spraying = status.is_spraying

        prev_status = spray_state.last_status.get(nozzle_id)

        if current_pressure is None:
            spray_state.update_last_status(status)
            continue

        if not is_spraying and current_pressure is not None:
            spray_state.resting_pressure[nozzle_id] = current_pressure
            spray_state.currently_spraying[nozzle_id] = False

        if prev_status and not prev_status["is_spraying"] and is_spraying:
            spray_state.spraying_since[nozzle_id] = datetime.utcnow()
            spray_state.currently_spraying[nozzle_id] = True
            baseline = spray_state.resting_pressure.get(nozzle_id, current_pressure)
            logger.info(
                f"[{nozzle_id}] 喷雾开始! 静止压力基线: {baseline:.3f} MPa, 当前压力: {current_pressure:.3f} MPa"
            )

        if is_spraying:
            baseline = spray_state.resting_pressure.get(nozzle_id)
            if baseline is None:
                spray_state.update_last_status(status)
                continue
            spray_duration = (datetime.utcnow() - spray_state.spraying_since.get(
                nozzle_id, datetime.utcnow() - timedelta(seconds=10)
            )).total_seconds()

            if spray_duration >= 3:
                is_abnormal, score = analyze_pressure_behavior(
                    nozzle_id, current_pressure, baseline, is_spraying
                )

                if is_abnormal:
                    spray_state.consecutive_failures[nozzle_id] += 1
                    logger.warning(
                        f"[{nozzle_id}] 压力异常! 基线:{baseline:.3f}, 当前:{current_pressure:.3f}, "
                        f"差值:{current_pressure - baseline:.3f}, 嫌疑度:{score:.1%}, "
                        f"连续异常次数:{spray_state.consecutive_failures[nozzle_id]}"
                    )

                    if (
                        spray_state.consecutive_failures[nozzle_id] >= CONSECUTIVE_FAILURES_THRESHOLD
                        and not status.is_suspected_blocked
                    ):
                        if not alert_crud.has_unresolved_blockage_alert(db, nozzle_id):
                            nozzle_crud.update_nozzle_blockage_status(
                                db, status.id, is_suspected_blocked=True, blockage_score=score
                            )
                            alert_crud.create_blockage_alert(
                                db, nozzle_id, score, baseline, current_pressure
                            )
                            logger.warning(
                                f"[{nozzle_id}] 已标记为疑似堵塞，嫌疑度 {score:.1%}，已创建检修告警"
                            )
                else:
                    spray_state.consecutive_failures[nozzle_id] = max(
                        0, spray_state.consecutive_failures[nozzle_id] - 1
                    )
                    if status.is_suspected_blocked and spray_state.consecutive_failures[nozzle_id] == 0:
                        nozzle_crud.update_nozzle_blockage_status(
                            db, status.id, is_suspected_blocked=False, blockage_score=0.0
                        )
                        logger.info(f"[{nozzle_id}] 压力恢复正常，堵塞标记已清除")

        if not is_spraying and nozzle_id in spray_state.currently_spraying:
            if spray_state.currently_spraying[nozzle_id]:
                logger.info(f"[{nozzle_id}] 喷雾结束")
            spray_state.currently_spraying[nozzle_id] = False
            if nozzle_id in spray_state.spraying_since:
                del spray_state.spraying_since[nozzle_id]
            spray_state.consecutive_failures[nozzle_id] = 0

        spray_state.update_last_status(status)


async def run_blockage_detector():
    """
    定时运行堵塞检测任务。
    """
    logger.info("喷头堵塞检测定时任务已启动，检测间隔: %d秒", CHECK_INTERVAL_SECONDS)

    first_run = True
    while True:
        try:
            db = SessionLocal()
            try:
                if first_run:
                    initialize_resting_pressures(db)
                    first_run = False
                check_nozzle_blockage(db)
            finally:
                db.close()
        except Exception as e:
            logger.exception(f"堵塞检测任务执行出错: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


def start_blockage_detector():
    """
    在后台线程中启动堵塞检测任务。
    """
    import threading

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_blockage_detector())

    thread = threading.Thread(target=_run, daemon=True, name="blockage-detector")
    thread.start()
    return thread
