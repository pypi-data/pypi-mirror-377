from upplib import *
from datetime import datetime, timezone, timedelta


def format_milliseconds(time_str):
    # 匹配小数点后的数字（至少1位），并捕获时区部分
    # param：2025-08-14T12:53:00.05382312323+07:00
    # return：2025-08-14T12:53:00.0538+07:00
    return re.sub(r'\.(\d+)([+-].*)?', lambda m: f".{m.group(1)[:4]}{m.group(2) or ''}", time_str)


def get_log_msg(contents: dict, time_is_necessary: bool = False) -> str:
    """
    time_is_necessary: 日志中的时间参数,是否是必须的
    获得日志
    """
    # time
    _time_ = None
    if '_time_' in contents:
        _time_ = format_milliseconds(contents['_time_'])
    if _time_ is None and 'time' in contents:
        _time_ = format_milliseconds(contents['time'])

    # level
    level = None
    if 'level' in contents:
        level = contents['level']

    # content
    content = None
    if 'content' in contents:
        content = contents['content']
    if content is None and 'message' in contents:
        content = contents['message']
    if content is None and 'msg' in contents:
        content = contents['msg']
    if content is not None:
        if 'time' in contents:
            content = format_milliseconds(contents['time']) + ' ' + content
        if len(str(content).split(' ')) >= 2:
            time_str = ' '.join(str(content).split(' ')[0:2])
            time_1 = to_datetime(time_str, error_is_none=True)
            if time_1 is not None:
                content = content[len(time_str):].strip()
            else:
                if not time_is_necessary:
                    # 如果 content 中，没有时间，那就把默认的时间，去掉
                    _time_ = None
        else:
            _time_ = None

    return ' '.join(filter(lambda s: s is not None, [_time_, level, content]))


def get_min_date_max_date_from_txt(file_name: str = '_start_time_end_time_str.txt',
                                   second: int | float = 0.1) -> tuple[datetime | None, datetime | None]:
    """
        从配置文件中获得 datetime
        file_name : 指定文件, 自动忽略掉文件中的 # 开头的行
        second : 获得时间，在 second 基础上，前后冗余多少秒
        获得日志
    """
    date_list = to_list_from_txt(file_name)
    date_list = list(filter(lambda x: len(x) > 0 and not str(x).strip().startswith('#'), date_list))
    if len(date_list) == 0:
        return None, None
    date_time_list = []
    for date_one in date_list:
        date_time_list.append(to_datetime(date_one))
    date_time_list.sort()
    min_time = to_datetime_add(date_time_list[0], seconds=-second)
    max_time = to_datetime_add(date_time_list[-1], seconds=second)
    return min_time, max_time


# # 测试代码
# if __name__ == "__main__":
#     a = to_datetime('2025/09/16 17:32:17.896 GMT+08:00')
#     print("解析结果:", a)
#     print("时区:", a.tzinfo)
#     print("ISO格式:", a.isoformat())
#
#     # 测试其他格式
#     print("\n测试其他格式:")
#     print(to_datetime('2025-09-16 17:32:17'))
#     print(to_datetime('1726488737'))  # 时间戳
#     print(to_datetime('2025-09-16T17:32:17Z'))  # ISO格式带UTC时区
#     print(to_datetime('2025/09/16 10:32:17 GMT-05:00'))  # 其他时区
#     print(to_datetime('2025-09-15 16:50:26+08:00'))  # 其他时区
#
#
#





















