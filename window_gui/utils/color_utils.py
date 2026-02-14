"""
颜色工具
"""

def get_cell_color(cell_data):
    """
    根据细胞数据获取颜色
    
    Args:
        cell_data: 细胞数据字典
        
    Returns:
        str: 十六进制颜色代码
    """
    # 从cell数据获取颜色属性
    color = cell_data.get('color', (0, 255, 0))
    
    if isinstance(color, tuple) and len(color) >= 3:
        r, g, b = color[:3]
        # 确保值在0-255范围内
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # 默认颜色：根据细胞名称生成确定性颜色
    name = cell_data.get('name', 'Cell')
    hash_val = sum(ord(c) for c in name) % 360
    return hsl_to_hex(hash_val, 70, 50)

def hsl_to_hex(h, s, l):
    """
    将HSL颜色转换为十六进制
    
    Args:
        h: 色相 (0-360)
        s: 饱和度 (0-100)
        l: 亮度 (0-100)
        
    Returns:
        str: 十六进制颜色代码
    """
    import colorsys
    
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0
    
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    
    return f"#{r:02x}{g:02x}{b:02x}"