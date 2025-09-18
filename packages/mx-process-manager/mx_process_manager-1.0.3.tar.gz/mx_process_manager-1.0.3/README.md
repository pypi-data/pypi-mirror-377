# 进程管理器

这是一个使用Python开发的现代化进程管理器，提供了直观的图形界面来管理系统进程。

![Example](https://raw.githubusercontent.com/darklee/process/refs/heads/master/assets/test.png)

## 功能特点

- 现代化的深色主题界面
- 树形结构显示进程关系
- 实时进程信息显示
- 进程搜索功能
- 自动刷新进程列表
- 进程终止功能（支持优雅终止和强制终止）

## 安装依赖

```bash
pipx install mx-process-manager
```

## 运行程序

```bash
mx-process-manager
```

## 使用说明

1. 界面顶部有搜索框，可以实时搜索进程
2. 进程列表以树形结构显示，可以展开/折叠查看子进程
3. 右键点击进程可以选择终止操作
4. 界面底部可以调整自动刷新间隔（默认5秒）
5. 进程信息包括：
   - PID（进程ID）
   - CPU时间
   - 启动时间
   - 父进程ID
   - 内存占用
   - 进程命令

## 注意事项

- 需要管理员/root权限才能终止某些系统进程
- 终止进程时会先尝试优雅终止（SIGTERM），10秒后如果进程仍在运行则强制终止（SIGKILL） 


