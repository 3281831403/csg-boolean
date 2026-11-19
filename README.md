# CSG 布尔：共面、退化与重三角化

两个实体做布尔差集时结果网格在共面处开裂：共面边没有进入裁剪链、退化三角形未剔除、切割面未重三角化、顶点焊接容差不对、面朝向不统一、中间结果无缓存、UV 直接复制、材质分组未重建、递归无深度上限、批量布尔无统一回滚。

## 目录结构

```
README.md
conftest.py
.gitignore
geometry/__init__.py
geometry/csg_boolean.py
tests/test_csg_boolean.py
```

## 当前状态

`geometry/csg_boolean.py` 中所有函数只保留签名与文档字符串，函数体统一
`raise NotImplementedError`。`tests/test_csg_boolean.py` 有 15 个参数化用例，
初始全部失败。

## 需要修复的 10 个问题

1. 共面边进入裁剪链
2. 退化三角形剔除
3. 切割面重新三角化
4. 按容差焊接顶点
5. 统一面朝向
6. 缓存中间布尔结果
7. 切割面 UV 重建
8. 按切割面重建材质分组
9. 递归深度上限
10. 批量布尔统一回滚

## 验收

```bash
python -m pytest -q
```

初始应得到 `15 failed`，且没有 collection error。实现 `geometry/csg_boolean.py`
后 15 条用例应全部通过。
