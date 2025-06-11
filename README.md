# Python Tower Defense Game

一个使用 Python 和 Tkinter 开发的塔防游戏。

## 环境要求

- Python 3.13.4 或更高版本
- Pillow (PIL) 库

### 关于 Pillow

Pillow 是 Python 图像处理库（Python Imaging Library，PIL）的一个分支，它提供了强大的图像处理功能：

- 图像打开、保存和转换
- 图像绘制和编辑
- 图像滤镜和特效
- 支持多种图像格式（PNG, JPEG, GIF, BMP 等）

在本游戏中，Pillow 主要用于：
- 加载和显示游戏图像资源
- 处理游戏界面的图像渲染
- 实现图像特效和动画

## 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/pythonGames.git
cd pythonGames
```

2. 创建并激活虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install Pillow
```

## 运行游戏

在项目目录下运行：
```bash
python3 tower_defense.py
```

## 注意事项

- 确保使用 Python 3.13.4 或更高版本
- 如果遇到 "No module named 'PIL'" 错误，请确保已安装 Pillow 库
- 游戏运行时可能会显示一些 IMK 相关的日志信息，这是正常的

## 游戏说明

- 使用鼠标左键点击地图放置防御塔
- 每个防御塔花费 50 金币
- 击败敌人获得 10 金币
- 每波结束后获得 50 金币奖励
- 敌人到达终点会减少生命值
- 生命值耗尽游戏结束

## 游戏特性

- 敌人沿着固定路径移动
- 防御塔自动攻击范围内的敌人
- 显示敌人血条
- 显示防御塔攻击范围
- 计分系统
- 波次系统 