# world/cleanup_glimmerdew.py
# 危险：此脚本用于批量删除对象！请谨慎使用。

from evennia import search_object
from evennia.utils import logger

# --- 配置需要清理的房间键名 ---
# 这是你之前脚本中定义的主要房间的键名
ROOM_KEYS_TO_CLEAN = [
    "林间空地",
    "幽暗树洞",
    "溪边小径",
    "密林边缘",
    "古树之下"
]

# (可选) 如果你给这些房间打了特定的标签，也可以按标签清理
# 例如：TAG_TO_CLEAN = "GlimmerdewForest"
# TAG_CATEGORY_TO_CLEAN = "region" # 如果标签有类别

if caller:
    caller.msg(f"--- 开始清理“荧露树林”的重复对象 ---")
    caller.msg(f"警告：此操作将删除所有找到的同名房间及其可能的内容（如出口）。")
    # 你可以在这里添加一个确认步骤，例如要求用户输入特定命令才继续

deleted_count = 0
for rkey in ROOM_KEYS_TO_CLEAN:
    # 查找所有具有该键名的对象（不区分类型，所以要小心）
    # 更安全的方式是也检查类型，例如 obj.is_typeclass("typeclasses.rooms.ForestRoom")
    matches = search_object(rkey)
    if not matches:
        if caller:
            caller.msg(f"未找到键名为 '{rkey}' 的对象。")
        continue

    if caller:
        caller.msg(f"找到 {len(matches)} 个键名为 '{rkey}' 的对象。准备删除...")

    for obj in matches:
        obj_id = obj.id
        obj_key = obj.key
        try:
            # 在删除前，可以取消所有角色对该房间的操控，如果需要的话
            # for char_content in obj.contents_get(content_type="character"):
            # if char_content.has_account:
            # char_content.account.unpuppet_object(char_content.account.sessions.get()[0])
            # char_content.move_to(None, quiet=True) # 移出房间

            obj.delete() # 实际删除操作
            deleted_count += 1
            if caller:
                caller.msg(f"已删除对象: {obj_key} (#{obj_id})")
        except Exception as e:
            logger.log_err(f"删除对象 {obj_key}(#{obj_id}) 时出错: {e}")
            if caller:
                caller.msg(f"删除对象 {obj_key}(#{obj_id}) 时出错: {e}")

if caller:
    caller.msg(f"--- “荧露树林”清理完成。共删除了 {deleted_count} 个主要房间对象。---")
    caller.msg(f"现在你可以安全地运行更新后的构建脚本了。")