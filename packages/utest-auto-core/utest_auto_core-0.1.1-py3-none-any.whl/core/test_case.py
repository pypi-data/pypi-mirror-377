#!/usr/bin/env python3
"""
简洁的QTAF风格测试框架

参考腾讯QTAF的设计理念，提供简洁清晰的测试步骤和断言管理
"""
import os
import re
import time
import traceback
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
import logging
from ubox_py_sdk import Device,LogcatTask

logger = logging.getLogger(__name__)


class TestStatus(str, Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class StepStatus(str, Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class FailureStrategy(str, Enum):
    """步骤失败策略枚举"""
    STOP_ON_FAILURE = "stop"  # 失败时停止执行后续步骤
    CONTINUE_ON_FAILURE = "continue"  # 失败时继续执行后续步骤


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    performance_data: Dict[str, Any] = field(default_factory=dict)
    logcat_data: Dict[str, Any] = field(default_factory=dict)  # logcat监控数据
    recording_data: Dict[str, Any] = field(default_factory=dict)  # 录制数据
    steps: List['StepResult'] = field(default_factory=list)

    def __post_init__(self):
        """计算测试持续时间"""
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


@dataclass
class StepResult:
    """步骤结果"""
    step_name: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self):
        """计算步骤持续时间"""
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


class TestCase(ABC):
    """测试用例基类"""

    def __init__(self, name: str, description: str = "", device: Device = None):
        self.test_context = None
        self.name = name
        self.description = description
        self.device: Device = device
        self.steps: List[StepResult] = []
        self.current_step: Optional[StepResult] = None
        self.context: Dict[str, Any] = {}

        # 测试用例级别的配置
        self.timeout: int = 300  # 默认5分钟超时
        self.retry_count: int = 0  # 默认不重试
        self.screenshot_on_failure: bool = True
        self.screenshot_on_success: bool = False
        self.failure_strategy: FailureStrategy = FailureStrategy.STOP_ON_FAILURE  # 断言失败策略

    def start_step(self, step_name: str, description: str = "") -> None:
        """
        开始一个测试步骤
        
        Args:
            step_name: 步骤名称
            description: 步骤描述
        """
        # 结束上一个步骤（如果存在）
        if self.current_step:
            self.end_step()

        # 开始新步骤
        self.current_step = StepResult(
            step_name=step_name,
            description=description,
            status=StepStatus.RUNNING,
            start_time=datetime.now()
        )

        logger.info(f"🚀 开始步骤: {step_name} - {description}")

    def end_step(self, status: StepStatus = None) -> None:
        """
        结束当前步骤
        
        Args:
            status: 步骤状态，如果为None则根据当前状态自动判断
        """
        if not self.current_step:
            return

        # 设置步骤结束时间
        self.current_step.end_time = datetime.now()

        # 设置步骤状态
        if status is not None:
            self.current_step.status = status
        elif self.current_step.status == StepStatus.RUNNING:
            # 如果还是运行状态，说明没有发生错误，标记为通过
            self.current_step.status = StepStatus.PASSED

        # 根据步骤状态决定是否截图
        if self.current_step.status == StepStatus.FAILED and self.screenshot_on_failure:
            self.take_screenshot_on_step_failure()
        elif self.current_step.status == StepStatus.PASSED and self.screenshot_on_success:
            self.take_screenshot_on_step_success()
        elif self.current_step.status == StepStatus.ERROR and self.screenshot_on_failure:
            self.take_screenshot_on_step_error()

        # 将步骤添加到步骤列表
        self.steps.append(self.current_step)
        self.current_step = None

    def assert_(self, message: str, condition: bool) -> None:
        """
        断言验证
        
        Args:
            message: 断言消息
            condition: 断言条件
        """
        if not self.current_step:
            raise RuntimeError("必须在start_step之后才能使用assert_")

        if not condition:
            error_msg = f"断言失败: {message}"
            logger.error(f"❌ {error_msg}")

            # 失败时截图
            if self.screenshot_on_failure:
                self.take_screenshot("assertion_failed")

            # 设置步骤失败
            self.current_step.status = StepStatus.FAILED
            self.current_step.error_message = error_msg

            # 根据失败策略处理
            if self.failure_strategy == FailureStrategy.STOP_ON_FAILURE:
                raise AssertionError(error_msg)
            # CONTINUE_ON_FAILURE 继续执行，不抛出异常
        else:
            logger.info(f"✅ 断言通过: {message}")

            # 成功时截图
            if self.screenshot_on_success:
                self.take_screenshot("assertion_passed")

    def assert_equal(self, message: str, actual: Any, expected: Any) -> None:
        """断言相等"""
        self.assert_(message, actual == expected)

    def assert_not_equal(self, message: str, actual: Any, expected: Any) -> None:
        """断言不相等"""
        self.assert_(message, actual != expected)

    def assert_contains(self, message: str, actual: Any, expected: Any) -> None:
        """断言包含"""
        self.assert_(message, expected in str(actual))

    def assert_not_contains(self, message: str, actual: Any, expected: Any) -> None:
        """断言不包含"""
        self.assert_(message, expected not in str(actual))

    def assert_true(self, message: str, condition: Any) -> None:
        """断言为真"""
        self.assert_(message, bool(condition))

    def assert_false(self, message: str, condition: Any) -> None:
        """断言为假"""
        self.assert_(message, not bool(condition))

    def assert_none(self, message: str, value: Any) -> None:
        """断言为空"""
        self.assert_(message, value is None)

    def assert_not_none(self, message: str, value: Any) -> None:
        """断言非空"""
        self.assert_(message, value is not None)

    def assert_greater_than(self, message: str, actual: Any, expected: Any) -> None:
        """断言大于"""
        self.assert_(message, actual > expected)

    def assert_less_than(self, message: str, actual: Any, expected: Any) -> None:
        """断言小于"""
        self.assert_(message, actual < expected)

    def log_info(self, message: str) -> None:
        """记录信息日志"""
        logger.info(f"📝 {message}")
        if self.current_step:
            self.current_step.logs.append(f"[INFO] {message}")

    def log_warning(self, message: str) -> None:
        """记录警告日志"""
        logger.warning(f"⚠️ {message}")
        if self.current_step:
            self.current_step.logs.append(f"[WARNING] {message}")

    def log_error(self, message: str) -> None:
        """记录错误日志"""
        logger.error(f"❌ {message}")
        if self.current_step:
            self.current_step.logs.append(f"[ERROR] {message}")

    def setup(self) -> None:
        """测试前置操作，子类可重写"""
        pass

    def teardown(self) -> None:
        """测试后置操作，子类可重写"""
        # 注意：监控任务的停止需要用户在测试用例中手动调用
        # 例如：self.stop_perf(), self.stop_record()
        # logcat和录制文件路径会在启动时自动记录到测试结果中
        pass

    def start_record(self) -> bool:
        """启动录制"""
        video_path = os.path.join(self.get_case_dir(), f"video_{time.strftime('%Y%m%d%H%M%S')}.mp4")
        res = self.device.record_start(video_path)
        if res:
            # 直接记录录制文件路径到测试结果中
            self.record_recording_data({'file_path': video_path})
            logger.info(f"测试用例 {self.name} 启动录制成功")
            return True
        else:
            logger.info(f"测试用例 {self.name} 启动录制失败")
            return False

    def start_perf(self, sub_process_name: str = '',
                   sub_window: str = '', case_name: str = '',
                   log_output_file: str = 'perf.json') -> bool:
        """启动性能监控
        
        注意：性能数据文件会在停止时由设备端写入到用例log目录，
        因此这里不记录任何文件路径，只负责触发开始。
        """
        res = self.device.perf_start(self.get_package_name(), sub_process_name,
                                     sub_window, case_name,
                                     log_output_file)
        if res:
            # 仅保存任务句柄，路径在停止时统一按固定位置读取
            self._perf_task = res
            logger.info(f"测试用例 {self.name} 性能监控已启动")
            return True
        else:
            logger.info(f"测试用例 {self.name} 性能监控启动失败")
            return False

    def start_logcat(self, clear: bool = False,
                               re_filter: Union[str, re.Pattern] = None) -> LogcatTask:
        """启动logcat收集"""
        output_file = os.path.join(self.get_log_dir(), "logcat.txt")
        res = self.device.logcat_start(output_file, clear, re_filter)
        if res:
            # 直接记录logcat文件路径到测试结果中
            self.record_logcat_data({'file_path': output_file})
            logger.info(f"测试用例 {self.name} logcat收集已启动，输出到: {output_file}")
            return res
        else:
            logger.info(f"测试用例 {self.name} logcat收集启动失败")
            return res

    def stop_perf(self) -> bool:
        """停止性能监控并收集数据
        
        设备端会在 self.get_log_dir()/perf.json 写入结果，
        这里在停止成功后按固定路径读取记录。
        """
        res = self.device.perf_stop(self.get_log_dir())
        if res:
            # 统一按固定文件路径读取
            self._perf_output_file = os.path.join(self.get_log_dir(), 'perf.json')
            self._collect_performance_data()
            logger.info(f"测试用例 {self.name} 性能监控已结束")
            return True
        else:
            logger.info(f"测试用例 {self.name} 性能监控结束失败")
            return False


    def stop_record(self) -> bool:
        """停止录制"""
        res = self.device.record_stop()
        if res:
            logger.info(f"测试用例 {self.name} 停止录制成功")
            return True
        else:
            logger.info(f"测试用例 {self.name} 停止录制失败")
            return False

    def set_test_context(self, context: Dict[str, Any]) -> None:
        """设置测试上下文信息"""
        self.test_context = context
        logger.info(f"测试用例 {self.name} 上下文信息已设置")
    
    def record_performance_data(self, data: Dict[str, Any]) -> None:
        """记录性能监控数据到测试结果中"""
        if not hasattr(self, '_test_result'):
            logger.warning("无法记录性能数据：测试结果对象不存在")
            return
        
        self._test_result.performance_data = data
        logger.info(f"测试用例 {self.name} 性能监控数据已记录")
    
    def record_logcat_data(self, data: Dict[str, Any]) -> None:
        """记录logcat数据到测试结果中"""
        if not hasattr(self, '_test_result'):
            logger.warning("无法记录logcat数据：测试结果对象不存在")
            return
        
        self._test_result.logcat_data = data
        logger.info(f"测试用例 {self.name} logcat数据已记录")

    
    def record_recording_data(self, data: Dict[str, Any]) -> None:
        """记录录制数据到测试结果中"""
        if not hasattr(self, '_test_result'):
            logger.warning("无法记录录制数据：测试结果对象不存在")
            return
        
        self._test_result.recording_data = data
        logger.info(f"测试用例 {self.name} 录制数据已记录")

    def _collect_performance_data(self) -> None:
        """收集并解析性能监控数据（perf.json）"""
        try:
            if hasattr(self, '_perf_output_file') and os.path.exists(self._perf_output_file):
                # 读取性能监控JSON文件
                with open(self._perf_output_file, 'r', encoding='utf-8') as f:
                    perf_data = json.load(f)

                # 基础元信息
                performance_data: Dict[str, Any] = {
                    'file_path': self._perf_output_file,
                    'file_size': os.path.getsize(self._perf_output_file),
                    'app_display_name': perf_data.get('AppDisplayName', ''),
                    'app_version': perf_data.get('AppVersion', ''),
                    'app_package_name': perf_data.get('AppPackageName', ''),
                    'device_model': perf_data.get('DeviceModel', ''),
                    'os_type': perf_data.get('OSType', ''),
                    'os_version': perf_data.get('OSVersion', ''),
                    'cpu_type': perf_data.get('CpuType', ''),
                    'gpu_type': perf_data.get('GpuType', ''),
                    'case_name': perf_data.get('CaseName', ''),
                    'data_start_time': perf_data.get('AbsDataStartTime', 0),
                    'collection_time': datetime.now().isoformat()
                }

                data_list: List[Dict[str, Any]] = perf_data.get('DataList', []) or []
                performance_data['data_count'] = len(data_list)

                if data_list:
                    # 将TimeStamp转为有序并计算时长（毫秒 -> 秒）
                    def parse_ts(v: Any) -> Optional[int]:
                        try:
                            return int(str(v))
                        except Exception:
                            return None

                    timestamps = [ts for ts in (parse_ts(x.get('TimeStamp')) for x in data_list) if ts is not None]
                    if timestamps:
                        duration_ms = max(timestamps) - min(timestamps)
                        performance_data['duration_sec'] = round(duration_ms / 1000.0, 2)

                    # FPS统计（过滤掉为None的项，保留0以统计掉帧情况）
                    fps_values = []
                    zero_fps_count = 0
                    for item in data_list:
                        fps = ((item.get('AndroidFps') or {}).get('fps'))
                        if fps is None:
                            continue
                        if float(fps) == 0:
                            zero_fps_count += 1
                        fps_values.append(float(fps))
                    if fps_values:
                        performance_data['avg_fps'] = sum(fps_values) / len(fps_values)
                        performance_data['max_fps'] = max(fps_values)
                        performance_data['min_fps'] = min(fps_values)
                        performance_data['zero_fps_count'] = zero_fps_count

                    # Jank统计
                    def safe_get(d: Dict[str, Any], *keys) -> Optional[float]:
                        cur = d
                        for k in keys:
                            if not isinstance(cur, dict) or k not in cur:
                                return None
                            cur = cur[k]
                        try:
                            return float(cur)
                        except Exception:
                            return None

                    big_jank = [safe_get(x, 'BigJank', 'BigJank') for x in data_list]
                    small_jank = [safe_get(x, 'SmallJank', 'SmallJank') for x in data_list]
                    stutter = [safe_get(x, 'Stutter', 'Stutter') for x in data_list]
                    bj = [v for v in big_jank if v is not None]
                    sj = [v for v in small_jank if v is not None]
                    st = [v for v in stutter if v is not None]
                    if bj:
                        performance_data['big_jank_sum'] = int(sum(bj))
                    if sj:
                        performance_data['small_jank_sum'] = int(sum(sj))
                    if st:
                        performance_data['stutter_avg'] = sum(st) / len(st)
                        performance_data['stutter_max'] = max(st)

                    # CPU/GPU统计
                    cpu_total = [safe_get(x, 'CpuUsage', 'TotalUsage') for x in data_list]
                    cpu_app = [safe_get(x, 'CpuUsage', 'AppUsage') for x in data_list]
                    gpu_usage = [safe_get(x, 'GpuUsage', 'GpuUsage') for x in data_list]
                    ct = [v for v in cpu_total if v is not None]
                    ca = [v for v in cpu_app if v is not None]
                    gu = [v for v in gpu_usage if v is not None]
                    if ct:
                        performance_data['cpu_total_avg'] = sum(ct) / len(ct)
                        performance_data['cpu_total_max'] = max(ct)
                    if ca:
                        performance_data['cpu_app_avg'] = sum(ca) / len(ca)
                        performance_data['cpu_app_max'] = max(ca)
                    if gu:
                        performance_data['gpu_avg'] = sum(gu) / len(gu)
                        performance_data['gpu_max'] = max(gu)

                    # 温度
                    cpu_temp = [safe_get(x, 'Temperature', 'CpuTemperature') for x in data_list]
                    bat_temp = [safe_get(x, 'Temperature', 'BatteryTemperature') for x in data_list]
                    ctp = [v for v in cpu_temp if v is not None]
                    btp = [v for v in bat_temp if v is not None]
                    if ctp:
                        performance_data['cpu_temp_avg'] = sum(ctp) / len(ctp)
                        performance_data['cpu_temp_max'] = max(ctp)
                    if btp:
                        performance_data['battery_temp_avg'] = sum(btp) / len(btp)
                        performance_data['battery_temp_max'] = max(btp)

                    # 功耗
                    cur_list = [safe_get(x, 'Power', 'Current') for x in data_list]
                    vol_list = [safe_get(x, 'Power', 'Voltage') for x in data_list]
                    pow_list = [safe_get(x, 'Power', 'Power') for x in data_list]
                    bat_level = [safe_get(x, 'Power', 'BatLevel') for x in data_list]
                    cl = [v for v in cur_list if v is not None]
                    vl = [v for v in vol_list if v is not None]
                    pl = [v for v in pow_list if v is not None]
                    bl = [int(v) for v in bat_level if v is not None]
                    if cl:
                        performance_data['power_current_avg'] = sum(cl) / len(cl)
                        performance_data['power_current_max'] = max(cl)
                    if vl:
                        performance_data['power_voltage_avg'] = sum(vl) / len(vl)
                        performance_data['power_voltage_max'] = max(vl)
                    if pl:
                        performance_data['power_power_avg'] = sum(pl) / len(pl)
                        performance_data['power_power_max'] = max(pl)
                    if bl:
                        performance_data['battery_level_last'] = bl[-1]

                    # 内存
                    mem = [safe_get(x, 'AndroidMemoryUsage', 'Memory') for x in data_list]
                    swap = [safe_get(x, 'AndroidMemoryUsage', 'SwapMemory') for x in data_list]
                    mv = [v for v in mem if v is not None]
                    sv = [v for v in swap if v is not None]
                    if mv:
                        performance_data['memory_avg'] = sum(mv) / len(mv)
                        performance_data['memory_max'] = max(mv)
                    if sv:
                        performance_data['swap_avg'] = sum(sv) / len(sv)
                        performance_data['swap_max'] = max(sv)

                    # 虚拟内存
                    vmem = [safe_get(x, 'VirtualMemory', 'VirtualMemory') for x in data_list]
                    vv = [v for v in vmem if v is not None]
                    if vv:
                        performance_data['vmem_avg'] = sum(vv) / len(vv)
                        performance_data['vmem_max'] = max(vv)

                    # 网络
                    up = [safe_get(x, 'NetworkUsage', 'UpSpeed') for x in data_list]
                    down = [safe_get(x, 'NetworkUsage', 'DownSpeed') for x in data_list]
                    upv = [v for v in up if v is not None]
                    dnv = [v for v in down if v is not None]
                    if upv:
                        performance_data['net_up_avg'] = sum(upv) / len(upv)
                        performance_data['net_up_max'] = max(upv)
                    if dnv:
                        performance_data['net_down_avg'] = sum(dnv) / len(dnv)
                        performance_data['net_down_max'] = max(dnv)

                # 写入测试结果
                self.record_performance_data(performance_data)
                logger.info(f"性能监控数据收集完成: {self._perf_output_file}")
            else:
                logger.warning("性能监控文件不存在，无法收集数据")
        except Exception as e:
            logger.error(f"收集性能监控数据失败: {e}")



    def apply_screenshot_config(self, screenshot_on_failure: bool = None, screenshot_on_success: bool = None) -> None:
        """
        应用截图配置
        
        Args:
            screenshot_on_failure: 失败时是否截图，None表示不修改
            screenshot_on_success: 成功时是否截图，None表示不修改
        """
        if screenshot_on_failure is not None:
            self.screenshot_on_failure = screenshot_on_failure
            logger.info(f"测试用例 {self.name} 失败时截图设置: {screenshot_on_failure}")

        if screenshot_on_success is not None:
            self.screenshot_on_success = screenshot_on_success
            logger.info(f"测试用例 {self.name} 成功时截图设置: {screenshot_on_success}")

    def get_device_serial(self) -> str:
        """获取设备序列号"""
        return self.test_context.get('serial_num', '') if hasattr(self, 'test_context') else ''

    def get_package_name(self) -> str:
        """获取测试包名"""
        return self.test_context.get('package_name', '') if hasattr(self, 'test_context') else ''

    def get_test_result_dir(self) -> str:
        """获取测试结果根目录"""
        if hasattr(self, 'test_context') and 'test_result_dir' in self.test_context:
            return self.test_context.get('test_result_dir')
        return './test_result'

    def get_case_base_dir(self) -> str:
        """获取用例基础目录: test_result/case/"""
        if hasattr(self, 'test_context') and 'case_base_dir' in self.test_context:
            return self.test_context.get('case_base_dir')
        return os.path.join(self.get_test_result_dir(), 'case')

    def get_log_base_dir(self) -> str:
        """获取日志基础目录: test_result/log/"""
        if hasattr(self, 'test_context') and 'log_base_dir' in self.test_context:
            return self.test_context.get('log_base_dir')
        return os.path.join(self.get_test_result_dir(), 'log')

    def get_case_dir(self) -> str:
        """获取当前用例的case目录:test_result/case/{用例名}/case/"""
        if hasattr(self, 'test_context') and 'case_dir' in self.test_context:
            return self.test_context.get('case_dir')
        return os.path.join(self.get_case_base_dir(), self.name)

    def get_case_pic_dir(self) -> str:
        """获取当前用例的case的目录:test_result/case/{用例名}/pic/"""
        if hasattr(self, 'test_context') and 'case_pic_dir' in self.test_context:
            return self.test_context.get('case_pic_dir')
        return os.path.join(self.get_case_base_dir(), self.name)

    def get_log_dir(self) -> str:
        """获取当前用例的log目录:test_result/case/{用例名}/log/"""
        if hasattr(self, 'test_context') and 'log_dir' in self.test_context:
            return self.test_context.get('log_dir')
        return os.path.join(self.get_log_base_dir(), self.name)

    def take_screenshot(self, pic_name: str = "screenshot") -> Optional[str]:
        """
        截取屏幕截图
        
        Args:
            pic_name: 截图文件名
        Returns:
            Optional[str]: 截图文件路径，失败时返回None
        """
        if not self.device:
            logger.warning("设备对象未初始化，无法截图")
            return None

        try:
            res = self.device.screenshot(pic_name, self.get_case_pic_dir())
            img_path = res["img_path"]
            # 将截图路径添加到当前步骤
            if self.current_step:
                self.current_step.screenshots.append(img_path)
            return img_path

        except Exception as e:
            logger.error(f"❌ 截图失败: {e}\n{traceback.format_exc()}")
            return None

    def take_screenshot_on_step_success(self) -> Optional[str]:
        """步骤成功时截图"""
        if not self.current_step:
            return None
        return self.take_screenshot("step_success")

    def take_screenshot_on_step_failure(self) -> Optional[str]:
        """步骤失败时截图"""
        if not self.current_step:
            return None
        return self.take_screenshot("step_failure")

    def take_screenshot_on_step_error(self) -> Optional[str]:
        """步骤错误时截图"""
        if not self.current_step:
            return None
        return self.take_screenshot("step_error")

    @abstractmethod
    def run_test(self) -> None:
        """运行测试用例，子类必须实现"""
        pass

    def execute(self, device, context: Dict[str, Any]) -> TestResult:
        """执行测试用例"""
        start_time = datetime.now()
        test_result = TestResult(
            test_name=self.name,
            status=TestStatus.RUNNING,
            start_time=start_time
        )

        try:
            logger.info(f"开始执行测试用例: {self.name} - {self.description}")

            # 保存设备对象到测试用例实例中
            self.device = device
            
            # 保存测试结果对象，供测试用例记录监控数据使用
            self._test_result = test_result

            # 设置测试上下文
            self.set_test_context(context)

            # 执行前置操作
            self.setup()

            # 执行测试用例
            self.run_test()

            # 执行后置操作
            self.teardown()

            # 结束最后一个步骤
            if self.current_step:
                self.end_step(StepStatus.PASSED)

            # 设置测试结果状态
            failed_steps = [s for s in self.steps if s.status == StepStatus.FAILED]
            if failed_steps:
                test_result.status = TestStatus.FAILED
                test_result.error_message = f"有 {len(failed_steps)} 个步骤失败"
            else:
                test_result.status = TestStatus.PASSED

            # 复制步骤结果
            test_result.steps = self.steps.copy()

        except Exception as e:
            test_result.status = TestStatus.ERROR
            test_result.error_message = str(e)
            test_result.error_traceback = traceback.format_exc()
            logger.error(f"测试用例异常: {self.name} - {e}\n{traceback.format_exc()}")

            # 结束当前步骤
            if self.current_step:
                self.current_step.error_message = str(e)
                self.end_step(StepStatus.ERROR)

            test_result.steps = self.steps.copy()

        finally:
            test_result.end_time = datetime.now()
            # 手动计算持续时间，因为__post_init__在对象创建时调用，那时end_time还是None
            if test_result.end_time and test_result.start_time:
                test_result.duration = (test_result.end_time - test_result.start_time).total_seconds()

            duration_str = f"{test_result.duration:.2f}" if test_result.duration is not None else "未知"
            logger.info(f"测试用例完成: {self.name}, 状态: {test_result.status.value}, 耗时: {duration_str}秒")

        return test_result


class TestSuite:

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.test_cases: List[TestCase] = []

    def add_test_case(self, test_case: TestCase) -> 'TestSuite':
        """添加测试用例"""
        self.test_cases.append(test_case)
        return self

    def execute(self, device, context: Dict[str, Any]) -> List[TestResult]:
        """执行测试套件"""
        results = []

        for test_case in self.test_cases:
            result = test_case.execute(device, context)
            results.append(result)

        return results
