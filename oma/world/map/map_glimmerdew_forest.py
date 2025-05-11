# oma/world/map_glimmerdew_forest.py

from evennia import create_object, search_object, DefaultRoom, DefaultExit
from evennia.utils import logger

# 尝试导入自定义房间类，如果失败则使用默认房间类
try:
    from typeclasses.rooms import ForestRoom
except ImportError:
    logger.log_warn("自定义房间类 'typeclasses.rooms.ForestRoom' 未找到, 将使用 'DefaultRoom' 作为替代。")
    ForestRoom = DefaultRoom

# -----------------------------------------------------------------------------
# 地图配置 (为每个新地图修改这部分)
# -----------------------------------------------------------------------------
MAP_NAME = "荧露树林"  # 用于日志/消息中的地图名称
UNIQUE_MAP_TAG = "map_glimmerdew_forest_obj"  # 此地图所有对象的唯一标签
UNIQUE_MAP_TAG_CATEGORY = "map_management"    # 此地图管理标签的类别

# -----------------------------------------------------------------------------
# 房间定义数据
# -----------------------------------------------------------------------------
ROOM_DEFINITIONS = {
    "林间空地": {
        "typeclass": ForestRoom,
        "desc": """
这里是一片开阔的林间空地，阳光透过稀疏的枝叶洒在长满青苔的地面上。
空气清新，带着淡淡的花香。四周相对安静，只有微风吹过树叶的沙沙声。
几条模糊的小径从空地向不同方向延伸出去。
        """,
        "tags": [("forest_spawn_point", "info"), ("GlimmerdewForest", "region")] # 示例标签
    },
    "幽暗树洞": {
        "typeclass": ForestRoom,
        "desc": """
你来到一个幽暗的树洞前，洞口被茂密的藤蔓半遮半掩。
洞内黑漆漆的，散发出一股潮湿的泥土和腐殖质的气味。
微风吹过洞口，发出呜呜的声响，让人有些不安。
        """,
        "tags": [("GlimmerdewForest", "region")]
    },
    "溪边小径": {
        "typeclass": ForestRoom,
        "desc": """
一条湿滑的小径沿着一条潺潺流淌的小溪蜿蜒向前。
溪水清澈见底，可以看到水底圆润的鹅卵石。
两岸长满了蕨类植物和不知名的野花，空气中充满了水汽。
        """,
        "tags": [("GlimmerdewForest", "region")]
    },
    "密林边缘": {
        "typeclass": ForestRoom,
        "desc": """
这里是森林中较为茂密的一块区域的边缘。
高大的树木枝叶交错，几乎遮蔽了所有的阳光，使得林下光线昏暗。
地上铺满了厚厚的落叶，踩上去沙沙作响。更深处似乎隐藏着未知的危险。
        """,
        "tags": [("GlimmerdewForest", "region")]
    },
    "古树之下": {
        "typeclass": ForestRoom,
        "desc": """
你站在一棵巨大的古树之下。这棵树异常粗壮，几个人都合抱不过来。
虬结的树根深深扎入土地，苍老的树皮上布满了苔藓和岁月的痕迹。
树冠遮天蔽日，阳光只能从叶缝中洒落点点光斑。气氛庄严而神秘。
        """,
        "tags": [("GlimmerdewForest", "region")]
    }
}

# -----------------------------------------------------------------------------
# 出口定义数据
# -----------------------------------------------------------------------------
EXIT_DEFINITIONS = [
    {
        "origin_room_key": "林间空地", "destination_room_key": "幽暗树洞",
        "exit_key": "北;north;n", "exit_desc": "一条小径向北蜿蜒，通往一个看起来有些阴暗的地方。",
        "reverse_exit_key": "南;south;s", "reverse_exit_desc": "回到南边的林间空地。"
    },
    {
        "origin_room_key": "林间空地", "destination_room_key": "溪边小径",
        "exit_key": "东;east;e", "exit_desc": "东边的小路似乎通向水源，可以听到微弱的水流声。",
        "reverse_exit_key": "西;west;w", "reverse_exit_desc": "向西可以返回林间空地。"
    },
    {
        "origin_room_key": "林间空地", "destination_room_key": "古树之下",
        "exit_key": "南;south;s", "exit_desc": "向南望去，可以看到一棵巨大的古树的轮廓。",
        "reverse_exit_key": "北;north;n", "reverse_exit_desc": "向北可以回到林间空地。"
    },
    {
        "origin_room_key": "林间空地", "destination_room_key": "密林边缘",
        "exit_key": "西;west;w", "exit_desc": "西边是茂密的森林边缘，光线在那里变得昏暗起来。",
        "reverse_exit_key": "东;east;e", "reverse_exit_desc": "东边是光线稍好一些的林间空地。"
    }
    # 你可以在这里为其他房间之间添加出口，例如从“幽暗树洞”到新房间等
]

# -----------------------------------------------------------------------------
# 辅助函数：清理由本地图脚本管理的对象
# -----------------------------------------------------------------------------
def cleanup_managed_objects(tag_to_delete, category_to_delete, caller_obj):
    """删除所有带有特定管理标签的对象。"""
    if caller_obj:
        caller_obj.msg(f"--- 开始为地图 '{MAP_NAME}' 清理托管对象 (标签: {tag_to_delete}:{category_to_delete}) ---")

    # 查找所有带有管理标签的对象 (房间、出口等)
    # search_object 可以按标签元组列表搜索
    objects_to_delete = search_object(tags=[(tag_to_delete, category_to_delete)])

    if not objects_to_delete:
        if caller_obj:
            caller_obj.msg("未找到需要清理的现有托管对象。")
        return 0 # 返回删除的数量

    deleted_count = 0
    for obj in objects_to_delete:
        obj_id_str = f"#{obj.id}" if obj.id else "(no id)"
        obj_key_str = obj.key if obj.key else "(no key)"
        try:
            # 安全检查：如果执行者恰好位于要删除的房间中，先将其移出
            if caller_obj and hasattr(caller_obj, "location") and caller_obj.location == obj:
                default_limbo = search_object(settings.DEFAULT_HOME, exact=True) # 使用 settings.DEFAULT_HOME
                if default_limbo and default_limbo[0] != obj : # 确保 Limbo 不是要删除的房间本身
                    caller_obj.move_to(default_limbo[0], quiet=True, move_hooks=False)
                    if caller_obj:
                        caller_obj.msg(f"你已从即将被删除的房间 {obj_key_str} 移至 Limbo。")
                else: # 无法安全移出，跳过删除此房间
                    if caller_obj:
                        caller_obj.msg(f"警告: 跳过删除你当前所在的房间 {obj_key_str}{obj_id_str}。")
                    continue
            
            obj.delete()
            deleted_count += 1
        except Exception as e:
            logger.log_err(f"删除对象 {obj_key_str}{obj_id_str} 时出错: {e}")
            if caller_obj:
                caller_obj.msg(f"删除对象 {obj_key_str}{obj_id_str} 时出错: {e}")

    if caller_obj:
        caller_obj.msg(f"--- 地图 '{MAP_NAME}' 清理完毕。共删除了 {deleted_count} 个托管对象。 ---")
    return deleted_count

# -----------------------------------------------------------------------------
# 主要脚本执行逻辑
# -----------------------------------------------------------------------------

# 步骤0: (可选) 清理此脚本先前创建的对象，以确保幂等性
# 将此设置为 False 可以跳过清理步骤，但再次运行时可能会遇到键名冲突（如果外部也创建了同名对象）
# 或者如果你想手动管理旧对象。
PERFORM_CLEANUP_BEFORE_BUILD = True
if PERFORM_CLEANUP_BEFORE_BUILD:
    # 'caller' 是 @batchcode 命令执行时可用的全局变量，指向执行该命令的角色
    cleanup_managed_objects(UNIQUE_MAP_TAG, UNIQUE_MAP_TAG_CATEGORY, caller)

# 用于存储已创建的房间对象，方便后续链接出口
created_rooms = {}

if caller:
    caller.msg(f"--- 开始构建/更新地图 '{MAP_NAME}' ---")

# 步骤1: 创建所有房间
for room_key_name, room_data in ROOM_DEFINITIONS.items():
    # 为所有由此脚本创建的房间添加统一的管理标签
    current_room_tags = room_data.get("tags", []).copy() # 复制以避免修改原始定义
    current_room_tags.append((UNIQUE_MAP_TAG, UNIQUE_MAP_TAG_CATEGORY))

    # 由于我们先执行了清理，这里可以直接创建，不需要复杂的“搜索-更新”逻辑
    # 如果跳过清理，则需要先搜索是否存在，存在则更新，不存在则创建
    room = create_object(
        room_data["typeclass"],
        key=room_key_name,
        attributes=[("desc", room_data["desc"].strip())],
        tags=current_room_tags
    )
    created_rooms[room_key_name] = room
    if caller:
        # 显示所有标签，包括管理标签
        tag_strings = [f"{tkey}:{tcat}" if tcat else tkey for tkey, tcat in room.tags.all(return_tuples=True)]
        caller.msg(f"已创建房间: {room_key_name} (#{room.id}) - 标签: {', '.join(tag_strings)}")


if caller:
    caller.msg("所有房间已创建。开始创建出口...")

# 步骤2: 创建所有出口
for exit_data in EXIT_DEFINITIONS:
    origin_room = created_rooms.get(exit_data["origin_room_key"])
    destination_room = created_rooms.get(exit_data["destination_room_key"])

    if origin_room and destination_room:
        # 为所有由此脚本创建的出口也添加统一的管理标签
        exit_tags = [(UNIQUE_MAP_TAG, UNIQUE_MAP_TAG_CATEGORY)]
        
        # 创建正向出口
        exit_attrs = [("desc", exit_data["exit_desc"])] if exit_data.get("exit_desc") else []
        create_object(
            DefaultExit, # 或你自定义的出口类型
            key=exit_data["exit_key"],
            location=origin_room,
            destination=destination_room,
            attributes=exit_attrs,
            tags=exit_tags
        )
        
        # 创建反向出口
        reverse_attrs = [("desc", exit_data["reverse_exit_desc"])] if exit_data.get("reverse_exit_desc") else []
        create_object(
            DefaultExit, # 或你自定义的出口类型
            key=exit_data["reverse_exit_key"],
            location=destination_room,
            destination=origin_room,
            attributes=reverse_attrs,
            tags=exit_tags
        )
        
        if caller:
            caller.msg(f"已创建双向出口: {origin_room.key} ({exit_data['exit_key']}) <-> {destination_room.key} ({exit_data['reverse_exit_key']})")
    else:
        missing_keys = []
        if not origin_room: missing_keys.append(exit_data["origin_room_key"])
        if not destination_room: missing_keys.append(exit_data["destination_room_key"])
        error_msg = f"创建出口失败，因为找不到房间: {', '.join(missing_keys)}"
        logger.log_warn(error_msg) # 记录到服务器日志
        if caller:
            caller.msg(f"错误: {error_msg}")

if caller:
    caller.msg(f"--- 地图 '{MAP_NAME}' 构建/更新脚本执行完毕！ ---")