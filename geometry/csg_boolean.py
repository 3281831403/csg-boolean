"""CSG 布尔：共面、退化与重三角化.

布尔差集的辅助集合：共面边并入裁剪链、退化三角形剔除、切割面重三角化、
顶点按容差焊接、绕序统一、中间结果缓存键、切割面 UV 重建、材质分组、
递归深度上限与批量提交。所有函数均为纯函数，不修改入参。
"""

import math


def _as_point(point):
    """把点统一成可哈希的元组，用于比较与去重。"""
    if isinstance(point, (list, tuple)):
        return tuple(_as_point(value) for value in point)
    return point


def _edge_key(edge):
    """边的去重键：保留边的方向与顶点顺序。"""
    return _as_point(edge)


def include_coplanar(edges, coplanar):
    """把共面边并入裁剪边集合，去重且保序。

    ``edges`` 与 ``coplanar`` 都是边的序列。
    结果按“先 edges、后 coplanar”的顺序展平，重复边只保留第一次出现。
    """
    merged = []
    seen = set()
    for edge in (edges or []):
        key = _edge_key(edge)
        if key not in seen:
            seen.add(key)
            merged.append(edge)
    for edge in (coplanar or []):
        key = _edge_key(edge)
        if key not in seen:
            seen.add(key)
            merged.append(edge)
    return merged


def _cross(a, b, c):
    """返回向量 AB 与 AC 的叉积（二维时为标量，三维时为向量）。"""
    ab = [b[i] - a[i] for i in range(len(a))]
    ac = [c[i] - a[i] for i in range(len(a))]
    if len(a) == 2:
        return ab[0] * ac[1] - ab[1] * ac[0]
    if len(a) == 3:
        return (
            ab[1] * ac[2] - ab[2] * ac[1],
            ab[2] * ac[0] - ab[0] * ac[2],
            ab[0] * ac[1] - ab[1] * ac[0],
        )
    raise ValueError("点坐标只支持二维或三维")


def _area2(tri):
    """三角形面积的二倍；退化时自然为 0，不做除法。"""
    if len(tri) < 3:
        return 0.0
    cross = _cross(tri[0], tri[1], tri[2])
    if isinstance(cross, tuple):
        return math.sqrt(sum(component * component for component in cross))
    return abs(cross)


def drop_degenerate(tris, eps):
    """剔除面积不超过 eps 的退化三角形。

    面积用叉积模长计算，全程不做归一化，因此不会出现除零。
    """
    kept = []
    for tri in (tris or []):
        if _area2(tri) / 2.0 > eps:
            kept.append(tri)
    return kept


def fan_triangulate(polygon):
    """对切割面多边形做扇形三角化。

    以首顶点为扇心，把 N 边形拆成 N-2 个三角形；不足三个点返回空表。
    """
    points = list(polygon or [])
    if len(points) < 3:
        return []
    if len(points) == 3:
        return [points]
    return [[points[0], points[i], points[i + 1]] for i in range(1, len(points) - 1)]


def _distance2(a, b):
    """两点欧氏距离的平方。"""
    return sum((a[i] - b[i]) ** 2 for i in range(len(a)))


def weld_vertices(points, tolerance):
    """按容差把相近顶点焊到同一个代表点。

    代表点取容差范围内第一个出现的点；容差为负时视为 0。输出与输入等长，
    便于保留三角形索引拓扑。
    """
    tol = max(float(tolerance), 0.0)
    representatives = []
    welded = []
    for point in (points or []):
        match = None
        for rep in representatives:
            if _distance2(rep, point) <= tol * tol:
                match = rep
                break
        if match is None:
            representatives.append(point)
            match = point
        welded.append(match)
    return welded


def _signed_area(tri):
    """三角形的有向面积；三维点投影到主轴平面后计算。

    叉积为零（退化）时返回 0，调用方不会因此除以任何量。
    """
    if len(tri) < 3:
        return 0.0
    pts = [_as_point(p) for p in tri]
    cross = _cross(pts[0], pts[1], pts[2])
    if not isinstance(cross, tuple):
        return cross / 2.0
    axis = max(range(3), key=lambda i: abs(cross[i]))
    u, v = (axis + 1) % 3, (axis + 2) % 3
    a, b, c = pts
    return (
        (b[u] - a[u]) * (c[v] - a[v]) - (b[v] - a[v]) * (c[u] - a[u])
    ) / 2.0


def fix_orientation(tris):
    """统一三角形绕序，使有向面积为正。

    面积严格为负时交换后两个顶点；零面积保持原样。
    """
    fixed = []
    for tri in (tris or []):
        tri = list(tri)
        if _signed_area(tri) < 0:
            tri[1], tri[2] = tri[2], tri[1]
        fixed.append(tri)
    return fixed


def cache_key(mesh_id, operation, depth):
    """中间结果缓存键包含网格、操作与深度。"""
    return "{}|{}|{}".format(mesh_id, operation, depth)


def rebuild_uv(uvs):
    """切割面 UV 重新裁到 [0,1]。

    逐分量夹紧，避免直接复制原始 UV 造成的拉伸；输出为普通列表。
    """
    return [
        [min(max(float(u), 0.0), 1.0), min(max(float(v), 0.0), 1.0)]
        for u, v in (uvs or [])
    ]


def group_materials(materials):
    """按切割面重建材质分组计数。"""
    counts = {}
    for material in (materials or []):
        counts[material] = counts.get(material, 0) + 1
    return counts


def depth_allowed(depth, limit):
    """递归深度不超过上限才继续分割。"""
    return depth <= limit


def commit_batch(results):
    """批量布尔全部成功才提交。

    任一项失败则整体不提交，返回 ``False``；空批次视为成功。
    """
    return all(bool(result) for result in (results or []))
