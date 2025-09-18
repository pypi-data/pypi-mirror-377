import pendulum as plm
from enum import Enum
from simtoolsz.utils import Number
from typing import NewType, Self, Optional, Callable
import re


__all__ = [
    'TimeConversion', 'DurationFormat', 'DURATIONTYPE',
    'covertChineseShort'
]

DURATIONTYPE = NewType('DURATIONTYPE', str | Number | plm.Duration)

class DurationFormat(Enum):
    """时间持续格式枚举类，提供各种时间格式化的标准格式"""
    
    SECONDS = 'seconds'
    MILLISECONDS = 'milliseconds'
    MINUTES = 'minutes'
    HOURS = 'hours'
    ISO8601 = 'iso8601'
    CHINESE = 'chinese'
    ENGLISH = 'english'
    COLON = 'colon-separated'
    DURATION = 'duration'
    
    def __str__(self) -> str:
        """返回格式的字符串表示"""
        return self.value
    
    def __repr__(self) -> str:
        """返回格式的详细字符串表示"""
        return f"DurationFormat.{self.name}"
    
    def __eq__(self, other: object) -> bool:
        """比较两个DurationFormat是否相等"""
        if not isinstance(other, DurationFormat):
            return False
        return self.value == other.value
    
    @classmethod
    def get_format(cls, format: str) -> Self:
        """根据字符串获取对应的DurationFormat枚举值
        
        Args:
            format: 格式字符串，不区分大小写
            
        Returns:
            DurationFormat: 对应的枚举值
            
        Raises:
            KeyError: 如果格式字符串无效
        """
        try:
            return cls.__members__[format.upper()]
        except KeyError:
            raise KeyError(f"无效的格式: {format}。可选值: {[f.value for f in cls]}")
    
    @classmethod
    def all_formats(cls) -> list[Self]:
        """获取所有可用的格式"""
        return list(cls)
    
    @classmethod
    def format_names(cls) -> list[str]:
        """获取所有格式的名称列表"""
        return [f.name for f in cls]
    
    @classmethod
    def format_values(cls) -> list[str]:
        """获取所有格式的值列表"""
        return [f.value for f in cls]
    
    @classmethod
    def which_format(cls, value:DURATIONTYPE, 
                        cast:str|None = None) -> Optional[Self]:
        """根据输入内容，自动判断属于哪种时间持续格式
        
        Args:
            value: 输入值，可以是字符串、数字或pendulum.Duration
            cast: 强制指定格式类型，如果提供则按指定类型判断
            
        Returns:
            DurationFormat: 对应的格式枚举，无法判断时返回None
        """
        # 如果指定了cast，按指定类型处理
        if cast is not None:
            try:
                target_format = cls.get_format(cast)
            except KeyError:
                return None
                
            # 输入为pendulum.Duration时，只能为duration类型
            if isinstance(value, plm.Duration):
                return target_format if target_format == cls.DURATION else None
                
            # 输入为Number类型时，不能作为人类可读格式
            if isinstance(value, (int, float)):
                if target_format.is_human_readable:
                    return None
                return target_format
                
            # 输入为str类型时
            if isinstance(value, str):
                # 如果是人类可读格式，直接返回
                if target_format.is_human_readable:
                    return target_format
                    
                # 尝试转换为数字，看是否可以作为时间单位格式
                try:
                    float(value)
                    return target_format if target_format.is_time_unit else None
                except (ValueError, TypeError):
                    return None
                    
            return None
            
        # 未指定cast时，自动判断类型
        # 处理pendulum.Duration类型
        if isinstance(value, plm.Duration):
            return cls.DURATION
            
        # 处理int类型，默认为seconds
        if isinstance(value, int):
            return cls.SECONDS
            
        # 处理float类型，默认为minutes
        if isinstance(value, float):
            return cls.MINUTES
            
        # 处理str类型，匹配人类可读格式
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
                
            # 中文格式：包含中文数字和时间单位
            if any(unit in value for unit in ['天', '小时', '分钟', '秒钟', '毫秒']):
                return cls.CHINESE
                
            # 英文格式：如 "1 day", "2 hours", "30 minutes"
            english_pattern = r'^\s*\d+(\.\d+)?\s*(days?|hours?|minutes?|seconds?|milliseconds?)\s*$'
            if re.match(english_pattern, value, re.IGNORECASE):
                return cls.ENGLISH
                
            # 冒号分隔格式：如 "01:30:45", "2:15"
            colon_pattern = r'^\s*\d{1,2}(:\d{1,2}){1,2}\s*$'
            if re.match(colon_pattern, value):
                return cls.COLON
                
            # ISO8601格式：如 "P1DT2H3M4S"
            iso_pattern = r'^P(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$'
            if re.match(iso_pattern, value.upper()):
                return cls.ISO8601
                
            # 尝试解析为数字，可能是时间单位格式
            try:
                float(value)
                # 如果是纯数字，默认为seconds
                return cls.SECONDS
            except (ValueError, TypeError):
                pass
                
        return None

    @property
    def is_time_unit(self) -> bool:
        """判断是否为时间单位格式"""
        return self.value in {self.SECONDS.value, self.MILLISECONDS.value, 
                             self.MINUTES.value, self.HOURS.value}
    
    @property
    def is_human_readable(self) -> bool:
        """判断是否为人可读格式"""
        return self.value in {self.CHINESE.value, self.ENGLISH.value, self.COLON.value}


class ConversionType(object) :
    __all__ = ['fit']
    def __init__(self, type: DurationFormat) -> None:
        self._type = type
    
    def _parse_to_duration(self, value: DURATIONTYPE) -> plm.Duration:
        """将各种格式的输入转换为pendulum.Duration"""
        if isinstance(value, plm.Duration):
            return value
        
        if isinstance(value, (int, float)):
            if self._type == DurationFormat.SECONDS:
                return plm.duration(seconds=value)
            elif self._type == DurationFormat.MILLISECONDS:
                return plm.duration(milliseconds=value)
            elif self._type == DurationFormat.MINUTES:
                return plm.duration(minutes=value)
            elif self._type == DurationFormat.HOURS:
                return plm.duration(hours=value)
            else:
                return plm.duration(seconds=value)  # 默认按秒处理
        
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("空字符串无法转换")
            
            # 处理ISO8601格式
            if self._type == DurationFormat.ISO8601:
                return self._parse_iso8601_duration(value)
            
            # 处理中文格式
            if self._type == DurationFormat.CHINESE:
                return self._parse_chinese_duration(value)
            
            # 处理英文格式
            if self._type == DurationFormat.ENGLISH:
                return self._parse_english_duration(value)
            
            # 处理冒号格式
            if self._type == DurationFormat.COLON:
                return self._parse_colon_duration(value)
            
            # 处理纯数字字符串
            try:
                num_value = float(value)
                return self._parse_to_duration(num_value)
            except ValueError:
                raise ValueError(f"无法解析字符串为数字: {value}")
        
        raise ValueError(f"不支持的输入类型: {type(value)}")
    
    def _parse_chinese_duration(self, value: str) -> plm.Duration:
        """解析中文时间格式"""
        import re
        
        total_seconds = 0
        matched = False
        
        # 天的匹配
        match = re.search(r'(\d+(?:\.\d+)?)\s*天', value)
        if match:
            total_seconds += float(match.group(1)) * 86400
            matched = True
        
        # 小时的匹配
        match = re.search(r'(\d+(?:\.\d+)?)\s*小时', value)
        if not match:
            match = re.search(r'(\d+(?:\.\d+)?)\s*时', value)
        if match:
            total_seconds += float(match.group(1)) * 3600
            matched = True
        
        # 分钟的匹配
        match = re.search(r'(\d+(?:\.\d+)?)\s*分钟', value)
        if not match:
            match = re.search(r'(\d+(?:\.\d+)?)\s*分', value)
        if match:
            total_seconds += float(match.group(1)) * 60
            matched = True
        
        # 秒的匹配
        match = re.search(r'(\d+(?:\.\d+)?)\s*秒钟', value)
        if not match:
            match = re.search(r'(\d+(?:\.\d+)?)\s*秒', value)
        if match:
            total_seconds += float(match.group(1)) * 1
            matched = True
        
        # 毫秒的匹配
        match = re.search(r'(\d+(?:\.\d+)?)\s*毫秒', value)
        if match:
            total_seconds += float(match.group(1)) * 0.001
            matched = True
        
        if not matched:
            # 尝试简单的数字解析
            try:
                return plm.duration(seconds=float(value))
            except ValueError:
                raise ValueError(f"无效的中文时间格式: {value}")
        
        return plm.duration(seconds=total_seconds)
    
    def _parse_english_duration(self, value: str) -> plm.Duration:
        """解析英文时间格式"""
        import re
        
        pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)'
        matches = re.findall(pattern, value)
        
        if not matches:
            raise ValueError(f"无效的英文时间格式: {value}")
        
        total_seconds = 0
        unit_mapping = {
            'days': 86400,
            'day': 86400,
            'hours': 3600,
            'hour': 3600,
            'minutes': 60,
            'minute': 60,
            'seconds': 1,
            'second': 1,
            'milliseconds': 0.001,
            'millisecond': 0.001
        }
        
        for num_str, unit in matches:
            num = float(num_str)
            unit_lower = unit.lower()
            if unit_lower in unit_mapping:
                total_seconds += num * unit_mapping[unit_lower]
            else:
                raise ValueError(f"未知的英文时间单位: {unit}")
        
        return plm.duration(seconds=total_seconds)
    
    def _parse_colon_duration(self, value: str) -> plm.Duration:
        """解析冒号时间格式"""
        parts = value.split(':')
        
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(float, parts)
            return plm.duration(minutes=minutes, seconds=seconds)
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(float, parts)
            return plm.duration(hours=hours, minutes=minutes, seconds=seconds)
        else:
            raise ValueError(f"无效的冒号时间格式: {value}")
    
    def _parse_iso8601_duration(self, value: str) -> plm.Duration:
        """解析ISO 8601持续时间格式"""
        import re
        
        value = value.strip()
        if not value.startswith('P'):
            raise ValueError(f"无效的ISO 8601格式: {value} (必须以P开头)")
        
        # 移除P前缀
        duration_str = value[1:]
        
        total_seconds = 0
        
        # 分离日期和时间部分
        if 'T' in duration_str:
            date_part, time_part = duration_str.split('T', 1)
        else:
            date_part = duration_str
            time_part = ''
        
        # 解析日期部分
        if date_part:
            # 匹配天
            day_match = re.search(r'(\d+(?:\.\d+)?)D', date_part)
            if day_match:
                total_seconds += float(day_match.group(1)) * 86400
            
            # 匹配周
            week_match = re.search(r'(\d+(?:\.\d+)?)W', date_part)
            if week_match:
                total_seconds += float(week_match.group(1)) * 7 * 86400
        
        # 解析时间部分
        if time_part:
            # 匹配小时
            hour_match = re.search(r'(\d+(?:\.\d+)?)H', time_part)
            if hour_match:
                total_seconds += float(hour_match.group(1)) * 3600
            
            # 匹配分钟
            minute_match = re.search(r'(\d+(?:\.\d+)?)M', time_part)
            if minute_match:
                total_seconds += float(minute_match.group(1)) * 60
            
            # 匹配秒
            second_match = re.search(r'(\d+(?:\.\d+)?)S', time_part)
            if second_match:
                total_seconds += float(second_match.group(1))
        
        if total_seconds == 0 and value != 'PT0S':
            raise ValueError(f"无效的ISO 8601格式: {value} (没有有效的时间单位)")
        
        return plm.duration(seconds=total_seconds)
    
    def _duration_to_target(self, duration: plm.Duration, target_format: DurationFormat) -> DURATIONTYPE:
        """将Duration转换为目标格式"""
        if target_format == DurationFormat.SECONDS:
            return duration.total_seconds()
        elif target_format == DurationFormat.MILLISECONDS:
            return duration.total_seconds() * 1000
        elif target_format == DurationFormat.MINUTES:
            return duration.total_seconds() / 60
        elif target_format == DurationFormat.HOURS:
            return duration.total_seconds() / 3600
        elif target_format == DurationFormat.ISO8601:
            return self._duration_to_iso(duration)
        elif target_format == DurationFormat.CHINESE:
            return self._duration_to_chinese(duration)
        elif target_format == DurationFormat.ENGLISH:
            return self._duration_to_english(duration)
        elif target_format == DurationFormat.COLON:
            return self._duration_to_colon(duration)
        elif target_format == DurationFormat.DURATION:
            return duration
        else:
            return duration.total_seconds()
    
    def _duration_to_iso(self, duration: plm.Duration) -> str:
        """将Duration转换为ISO 8601格式"""
        total_seconds = duration.total_seconds()
        
        # 如果为零持续时间
        if total_seconds == 0:
            return "PT0S"
        
        # 获取Duration的各个分量
        days = duration.days
        
        # 计算剩余的时间分量
        remaining_seconds = total_seconds - (days * 86400)
        hours = int(remaining_seconds // 3600)
        remaining_seconds %= 3600
        minutes = int(remaining_seconds // 60)
        seconds = remaining_seconds % 60
        
        # 构建ISO 8601格式的各个部分
        parts = []
        
        # 处理天数
        if days != 0:
            parts.append(f"{days}D")
        
        # 处理时间部分
        time_parts = []
        if hours != 0:
            time_parts.append(f"{hours}H")
        if minutes != 0:
            time_parts.append(f"{minutes}M")
        if seconds != 0:
            # 处理小数秒
            if seconds.is_integer():
                if int(seconds) != 0:
                    time_parts.append(f"{int(seconds)}S")
            else:
                # 移除末尾的零和小数点
                seconds_str = f"{seconds:.6f}".rstrip('0').rstrip('.')
                time_parts.append(f"{seconds_str}S")
        
        # 组合结果
        result = "P"
        
        if parts and time_parts:
            # 既有日期部分又有时间部分
            result += "".join(parts) + "T" + "".join(time_parts)
        elif parts:
            # 只有日期部分
            result += "".join(parts)
        elif time_parts:
            # 只有时间部分
            result += "T" + "".join(time_parts)
        
        return result
    
    def _duration_to_chinese(self, duration: plm.Duration) -> str:
        """将Duration转换为中文格式"""
        total_seconds = duration.total_seconds()
        
        if total_seconds == 0:
            return "0秒钟"
        
        parts = []
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0:
            parts.append(f"{seconds}秒钟")
        if milliseconds > 0:
            parts.append(f"{milliseconds}毫秒")
        
        return "".join(parts) if parts else "0秒钟"
    
    def _duration_to_english(self, duration: plm.Duration) -> str:
        """将Duration转换为英文格式"""
        total_seconds = duration.total_seconds()
        
        if total_seconds == 0:
            return "0 seconds"
        
        parts = []
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        if milliseconds > 0:
            parts.append(f"{milliseconds} millisecond{'s' if milliseconds != 1 else ''}")
        
        return " ".join(parts) if parts else "0 seconds"
    
    def _duration_to_colon(self, duration: plm.Duration) -> str:
        """将Duration转换为冒号格式"""
        total_seconds = duration.total_seconds()
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def fit(self, dest: DurationFormat) -> Callable[[DURATIONTYPE], DURATIONTYPE]:
        """
        返回一个函数，该函数可以将当前类型的值转换为目标格式
        
        Args:
            dest: 目标格式
            
        Returns:
            转换函数: DURATIONTYPE -> DURATIONTYPE
        """
        def converter(value: DURATIONTYPE) -> DURATIONTYPE:
            try:
                # 将输入值转换为Duration
                duration = self._parse_to_duration(value)
                # 将Duration转换为目标格式
                return self._duration_to_target(duration, dest)
            except Exception as e:
                raise ValueError(f"转换失败: {e}")
        
        return converter

class TimeConversion(object) :
    """
    时间转换类
    
    支持不同时间格式之间的转换，包括秒、毫秒、分钟、小时、ISO8601、中文、英文和冒号格式。
    """
    def __init__(self, time:DURATIONTYPE, 
                 inFormat:str|DurationFormat|None = None) -> None :
        self._time = time
        if isinstance(inFormat, str):
            self._Type = DurationFormat.get_format(inFormat)
        elif isinstance(inFormat, DurationFormat):
            self._Type = inFormat
        else:
            self._Type = DurationFormat.which_format(time)
        if self._Type is None:
            raise ValueError(f"无法确定时间持续格式: {time}")
        self._convType = ConversionType(self._Type)
    
    def convert(self, format:str|DurationFormat) -> DURATIONTYPE :
        """
        将当前时间值转换为目标格式
        
        Args:
            format: 目标格式，可以是字符串或DurationFormat枚举
            
        Returns:
            转换后的时间值，类型取决于目标格式
            
        Examples:
            >>> tc = TimeConversion("1天")
            >>> tc.convert("seconds")
            86400
            >>> tc.convert(DurationFormat.ENGLISH)
            "1 day"
        """
        if isinstance(format, str):
            target_format = DurationFormat.get_format(format)
        elif isinstance(format, DurationFormat):
            target_format = format
        else:
            raise ValueError(f"无效的目标格式: {format}")
        
        converter = self._convType.fit(target_format)
        return converter(self._time)
    
    def set_format(self, inFormat: str|DurationFormat) -> None:
        """
        设置新的输入格式
        
        Args:
            inFormat: 新的输入格式
        """
        if isinstance(inFormat, str):
            new_type = DurationFormat.get_format(inFormat)
        elif isinstance(inFormat, DurationFormat):
            new_type = inFormat
        else:
            raise ValueError(f"无效的格式: {inFormat}")
        if new_type is None:
            raise ValueError(f"无法设定时间持续格式: {inFormat}")
        
        self._Type = new_type
        self._convType = ConversionType(self._Type)
    
    def get_format(self) -> DurationFormat:
        """获取当前输入格式"""
        return self._Type
    
    def __repr__(self) -> str:
        return f"TimeConversion({self._time}, format={self._Type})"
    
    def __str__(self) -> str:
        return f"TimeConversion({self._time}, format={self._Type})"


def covertChineseShort(time:DURATIONTYPE) -> str :
    """
    将时间转换为中文短格式，即最小时间单位为秒
    """
    tc = TimeConversion(time)
    middle = round(tc.convert("seconds"))
    tc = TimeConversion(middle, "seconds")
    res = tc.convert("chinese")
    res = res.replace("钟", "")
    return res
