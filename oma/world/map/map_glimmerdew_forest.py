# oma/world/map_glimmerdew_forest.py

from evennia import create_object, DefaultRoom, DefaultExit
from evennia.utils import logger
# 导入 evennia.utils.search 模块以访问 search_object
import evennia.utils.search
# 导入 evennia.search_tag 函数
from evennia import search_tag # <--- 新增导入
from django.conf import settings

# 尝试导入自定义房间类，如果失败则使用默认房间类
try:
    from typeclasses.rooms import ForestRoom
except ImportError:
    logger.log_warn("自定义房间类 'typeclasses.rooms.ForestRoom' 未找到, 将使用 'DefaultRoom' 作为替代。")
    ForestRoom = DefaultRoom

# -----------------------------------------------------------------------------
# 地图配置 (为每个新地图修改这部分)
# -----------------------------------------------------------------------------
MAP_NAME = "荧露树林"
UNIQUE_MAP_TAG = "map_glimmerdew_forest_obj"
UNIQUE_MAP_TAG_CATEGORY = "map_management"

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
        "tags": [("forest_spawn_point", "info"), ("GlimmerdewForest", "region")]
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
        "exit_key_string": "北;north;n", 
        "exit_desc": "一条小径向北蜿蜒，通往一个看起来有些阴暗的地方。",
        "reverse_exit_key_string": "南;south;s", 
        "reverse_exit_desc": "回到南边的林间空地。"
    },
    {
        "origin_room_key": "林间空地", "destination_room_key": "溪边小径",
        "exit_key_string": "东;east;e",
        "exit_desc": "东边的小路似乎通向水源，可以听到微弱的水流声。",
        "reverse_exit_key_string": "西;west;w",
        "reverse_exit_desc": "向西可以返回林间空地。"
    },
    {
        "origin_room_key": "林间空地", "destination_room_key": "古树之下",
        "exit_key_string": "南;south;s",
        "exit_desc": "向南望去，可以看到一棵巨大的古树的轮廓。",
        "reverse_exit_key_string": "北;north;n",
        "reverse_exit_desc": "向北可以回到林间空地。"
    },
    {
        "origin_room_key": "林间空地", "destination_room_key": "密林边缘",
        "exit_key_string": "西;west;w",
        "exit_desc": "西边是茂密的森林边缘，光线在那里变得昏暗起来。",
        "reverse_exit_key_string": "东;east;e",
        "reverse_exit_desc": "东边是光线稍好一些的林间空地。"
    }
]

# -----------------------------------------------------------------------------
# 辅助函数：清理由本地图脚本管理的对象
# -----------------------------------------------------------------------------
def cleanup_managed_objects(tag_key_to_delete, tag_category_to_delete, caller_obj):
    """删除所有带有特定管理标签和类别的对象。"""
    if caller_obj:
        caller_obj.msg(f"--- 开始为地图 '{MAP_NAME}' 清理托管对象 (标签: {tag_key_to_delete}:{tag_category_to_delete}) ---")

    # 使用 evennia.search_tag() 进行搜索
    objects_to_delete = search_tag(key=tag_key_to_delete, category=tag_category_to_delete) # <--- 修改在这里

    if not objects_to_delete:
        if caller_obj:
            caller_obj.msg(f"未找到任何带有标签 '{tag_key_to_delete}:{tag_category_to_delete}' 的托管对象。")
        return 0
        
    if caller_obj:
        caller_obj.msg(f"找到 {len(objects_to_delete)} 个带有标签 '{tag_key_to_delete}:{tag_category_to_delete}' 的托管对象准备删除。")

    deleted_count = 0
    for obj in objects_to_delete:
        obj_id_str = f"#{obj.id}" if obj.id else "(no id)"
        obj_key_str = obj.key if obj.key else "(no key)"
        try:
            if caller_obj and hasattr(caller_obj, "location") and caller_obj.location == obj:
                default_home_obj_list = evennia.utils.search.search_object(settings.DEFAULT_HOME, exact=True)
                if default_home_obj_list and default_home_obj_list[0] != obj:
                    caller_obj.move_to(default_home_obj_list[0], quiet=True, move_hooks=False)
                    if caller_obj:
                        caller_obj.msg(f"你已从即将被删除的房间 {obj_key_str} 移至 {default_home_obj_list[0].key}。")
                else:
                    if caller_obj:
                        caller_obj.msg(f"警告: 跳过删除你当前所在的房间 {obj_key_str}{obj_id_str} (无法安全移至默认房间)。")
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
# 辅助函数：解析出口键字符串并添加别名
# -----------------------------------------------------------------------------
def _parse_exit_key_string(key_string):
    """
    解析包含主名和别名（用分号分隔）的字符串。
    返回 (main_key, list_of_aliases)
    """
    parts = [part.strip() for part in key_string.split(';') if part.strip()]
    if not parts:
        return None, []
    main_key = parts[0]
    aliases = parts[1:]
    return main_key, aliases

# -----------------------------------------------------------------------------
# 主要脚本执行逻辑
# -----------------------------------------------------------------------------
# 'caller' 是 @batchcode 命令执行时可用的全局变量，指向执行该命令的角色

PERFORM_CLEANUP_BEFORE_BUILD = True
if PERFORM_CLEANUP_BEFORE_BUILD:
    cleanup_managed_objects(UNIQUE_MAP_TAG, UNIQUE_MAP_TAG_CATEGORY, caller)

created_rooms = {}

if caller:
    caller.msg(f"--- 开始构建/更新地图 '{MAP_NAME}' ---")

# 步骤1: 创建所有房间
for room_key_name, room_data in ROOM_DEFINITIONS.items():
    base_tags = room_data.get("tags", []).copy() 
    current_room_tags = base_tags + [(UNIQUE_MAP_TAG, UNIQUE_MAP_TAG_CATEGORY)]
    
    room = create_object(
        room_data["typeclass"],
        key=room_key_name,
        attributes=[("desc", room_data["desc"].strip())],
        tags=current_room_tags
    )
    created_rooms[room_key_name] = room
    if caller:
        tag_tuples = room.tags.all(return_key_and_category=True)
        tag_strings = [f"{tkey}:{tcat}" if tcat else tkey for tkey, tcat in tag_tuples]
        caller.msg(f"已创建房间: {room_key_name} (#{room.id}) - 标签: {', '.join(tag_strings)}")


if caller:
    caller.msg("所有房间已创建。开始创建出口...")

# 步骤2: 创建所有出口
for exit_data in EXIT_DEFINITIONS:
    origin_room = created_rooms.get(exit_data["origin_room_key"])
    destination_room = created_rooms.get(exit_data["destination_room_key"])

    if origin_room and destination_room:
        exit_tags = [(UNIQUE_MAP_TAG, UNIQUE_MAP_TAG_CATEGORY)]
        
        fwd_main_key, fwd_aliases = _parse_exit_key_string(exit_data["exit_key_string"])
        if fwd_main_key: 
            exit_attrs_forward = [("desc", exit_data["exit_desc"])] if exit_data.get("exit_desc") else []
            fwd_exit_obj = create_object(
                DefaultExit, 
                key=fwd_main_key, 
                location=origin_room,
                destination=destination_room,
                attributes=exit_attrs_forward,
                tags=exit_tags
            )
            if fwd_aliases: 
                fwd_exit_obj.aliases.batch_add(*fwd_aliases)
        
        rev_main_key, rev_aliases = _parse_exit_key_string(exit_data["reverse_exit_key_string"])
        if rev_main_key: 
            exit_attrs_reverse = [("desc", exit_data["reverse_exit_desc"])] if exit_data.get("reverse_exit_desc") else []
            rev_exit_obj = create_object(
                DefaultExit,
                key=rev_main_key, 
                location=destination_room,
                destination=origin_room,
                attributes=exit_attrs_reverse,
                tags=exit_tags
            )
            if rev_aliases: 
                rev_exit_obj.aliases.batch_add(*rev_aliases)
            
            if caller and fwd_main_key and rev_main_key : 
                caller.msg(f"已创建双向出口: {origin_room.key} ({fwd_main_key}) <-> {destination_room.key} ({rev_main_key})")
        
    else:
        missing_keys = []
        if not origin_room: missing_keys.append(exit_data["origin_room_key"])
        if not destination_room: missing_keys.append(exit_data["destination_room_key"])
        error_msg = f"创建出口失败，因为找不到房间: {', '.join(missing_keys)}"
        logger.log_warn(error_msg)
        if caller:
            caller.msg(f"错误: {error_msg}")

if caller:
    caller.msg(f"--- 地图 '{MAP_NAME}' 构建/更新脚本执行完毕！ ---")
