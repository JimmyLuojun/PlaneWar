# 飞机大战 (Plane War)

一个简单的2D飞机射击游戏，使用Python和Pygame开发。

## 游戏特点

- 玩家控制飞机躲避敌机并射击
- 多种敌机类型，包括普通敌机和Boss敌机
- 道具系统（双弹、护盾、速度提升）
- 分数系统
- 生命值系统

## 安装说明

1. 确保已安装Python 3.6或更高版本
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 运行游戏

```bash
python main.py
```

## 游戏控制

- 方向键：移动飞机
- 空格键：发射子弹
- ESC键：退出游戏

## 文件结构

- `main.py`: 主程序，包含游戏主循环和场景管理
- `player.py`: 玩家飞机类
- `enemy.py`: 敌机类（以及Boss敌人类）
- `bullet.py`: 子弹类
- `powerup.py`: 道具类
- `settings.py`: 配置文件，存放常量参数 