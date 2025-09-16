# Countdown
python第三方库，实现到达目标时间执行函数


# 使用
```python
from FuyaoCountdown.countdown import Countdown


def job():
    print("job is running")


if __name__ == '__main__':
    cd = Countdown("2025-09-16", 5, 20)

    cd.threadExecutor(True, job)


```

## 参数说明
```text

Countdown(
    date: str 日期,如 "2025-09-16",
    hour: int 小时,如 5
    minute: int 分钟,如 20
    second: int 秒,如 0
)

Countdown.threadExecutor(
    useThread: bool 是否启用新线程
    job: Callable[..., Any]  可调用的任意对象/函数(任务对象)
    jobArgs: tuple  任务对象所需的参数
)

```


# 项目结构
```text
Countdown  项目名
    src  源代码
        FuyaoCountdown  软件包
    pyproject.toml  打包信息
    README.md  说明文件
    


```


# 更新日志

## v0.0.1
1.支持新线程执行任务