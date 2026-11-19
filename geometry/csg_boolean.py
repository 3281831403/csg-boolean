"""CSG 布尔：共面、退化与重三角化：待实现的核心模块。"""


def include_coplanar(edges, coplanar):
    """把共面边并入裁剪边集合，去重且保序。"""
    raise NotImplementedError

def drop_degenerate(tris, eps):
    """剔除面积不超过 eps 的退化三角形。"""
    raise NotImplementedError

def fan_triangulate(polygon):
    """对切割面多边形做扇形三角化。"""
    raise NotImplementedError

def weld_vertices(points, tolerance):
    """按容差把相近顶点焊到同一个代表点。"""
    raise NotImplementedError

def fix_orientation(tris):
    """统一三角形绕序，使有向面积为正。"""
    raise NotImplementedError

def cache_key(mesh_id, operation, depth):
    """中间结果缓存键包含网格、操作与深度。"""
    raise NotImplementedError

def rebuild_uv(uvs):
    """切割面 UV 重新裁到 [0,1]。"""
    raise NotImplementedError

def group_materials(materials):
    """按切割面重建材质分组计数。"""
    raise NotImplementedError

def depth_allowed(depth, limit):
    """递归深度不超过上限才继续分割。"""
    raise NotImplementedError

def commit_batch(results):
    """批量布尔全部成功才提交。"""
    raise NotImplementedError
