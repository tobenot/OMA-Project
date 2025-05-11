# typeclasses/characters.py

from evennia.objects.objects import DefaultCharacter
from evennia.utils import logger
from evennia import search_tag # 用于按标签搜索
import evennia.utils.search # 用于搜索 DEFAULT_HOME
from django.conf import settings # 用于 DEFAULT_HOME
import random

# 这是一个占位符，因为你的原始代码引用了 .objects.ObjectParent
# 如果你在 .objects 文件中有这个类的定义，请确保它是正确的。
# 如果 PrimordialCharacter 不需要它，这个占位符可以被更简单的基类替代或移除。
class ObjectParent: # Placeholder
    """A base class for other object types."""
    pass


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.
    """
    pass


class PrimordialCharacter(DefaultCharacter):
    """
    This class represents the player character in the "茹毛饮血" (Primordial) setting.
    It includes basic attributes and needs for survival.
    """
    def at_object_creation(self):
        """
        Called only once, when the object is first created.
        This sets up the character's initial state and flags it for initial spawn.
        """
        super().at_object_creation()
        self.db.desc = "一个身上被藤蔓覆盖的人类，看起来很瘦弱，眼神中带着一丝警惕和茫然。"
        self.db.strength = 5
        self.db.agility = 5
        self.db.constitution = 5
        self.db.perception = 5
        self.db.max_hp = 50
        self.db.current_hp = 50
        self.db.attack_power = 5
        self.db.defense = 1
        self.db.attack_speed = 2.5
        self.db.hunger = 100
        self.db.thirst = 100
        self.db.temperature = 37.0
        self.db.stamina = 100
        self.db.skill_cooldowns = {}
        self.db.is_in_combat = False
        self.db.combat_target = None
        self.db.needs_initial_spawn = True
        logger.log_infomsg(f"PrimordialCharacter {self.key} (ID: {self.id}) created. Flagged for initial spawn.")

    def _find_and_move_to_spawn_point(self, character_message, fallback_message):
        """
        Helper function to find a spawn point and move the character.
        Used for both initial spawn and respawn after death.
        Ensures "look" happens after the character_message.
        """
        spawn_tag_key = "forest_spawn_point"
        spawn_tag_category = "info"
        
        logger.log_infomsg(f"Character {self.key} attempting to find spawn location with tag '{spawn_tag_key}:{spawn_tag_category}'.")
        
        tagged_objects = search_tag(key=spawn_tag_key, category=spawn_tag_category)
        possible_spawn_locations = []
        if tagged_objects:
            for obj in tagged_objects:
                if obj.is_typeclass("typeclasses.rooms.ForestRoom", exact=False):
                    possible_spawn_locations.append(obj)
        
        if not possible_spawn_locations:
            logger.log_infomsg(
                f"No spawn locations found with '{spawn_tag_key}:{spawn_tag_category}'. "
                f"Trying with key only: '{spawn_tag_key}'."
            )
            tagged_objects_key_only = search_tag(key=spawn_tag_key)
            if tagged_objects_key_only:
                for obj in tagged_objects_key_only:
                    if obj.is_typeclass("typeclasses.rooms.ForestRoom", exact=False):
                        possible_spawn_locations.append(obj)
                        logger.log_infomsg(f"Found fallback spawn location by key only: {obj.key}")

        if possible_spawn_locations:
            spawn_location = random.choice(possible_spawn_locations)
            logger.log_infomsg(f"Character {self.key} (ID: {self.id}): Performing spawn/respawn to {spawn_location.key} (ID: {spawn_location.id}).")
            
            self.msg(character_message)
            
            if self.location != spawn_location:
                self.move_to(spawn_location, quiet=False, move_hooks=True) # quiet=False makes the character "look"
            else:
                # Already at the target location. Force a look to ensure view is current.
                self.execute_cmd("look") 
            
            return True # Spawn successful
        
        # If no possible_spawn_locations were found (fallback logic)
        logger.log_warnmsg(
            f"Character {self.key} (ID: {self.id}): "
            f"No valid spawn points found with tag. Attempting fallback to DEFAULT_HOME."
        )
        
        try:
            limbo_obj_list = evennia.utils.search.search_object(settings.DEFAULT_HOME, exact=True)
            if limbo_obj_list:
                limbo = limbo_obj_list[0]
                if self.location != limbo:
                    self.move_to(limbo, quiet=False, move_hooks=True) # This triggers a "look"
                    logger.log_infomsg(f"Moved {self.key} to Fallback Location (DEFAULT_HOME: {limbo.key}).")
                else: # Already in Limbo
                    self.execute_cmd("look") # Refresh view of Limbo
                    logger.log_infomsg(f"{self.key} is already in Fallback Location (DEFAULT_HOME: {limbo.key}).")
            else: # Limbo not found
                logger.log_warnmsg(f"Could not find Fallback Location (settings.DEFAULT_HOME) for {self.key}.")
                if self.location: 
                    self.execute_cmd("look") # Show current location

        except Exception as e:
            logger.log_errmsg(f"Error moving {self.key} to Fallback Location (DEFAULT_HOME): {e}")
            if self.location:
                self.execute_cmd("look") # Show current location after error

        self.msg(fallback_message) # Send fallback message AFTER attempting to move/look at Limbo or current location
        return False # Spawn not successful at intended forest point


    def at_post_puppet(self, **kwargs):
        """
        Called every time the character is puppeted by an account (e.g. login, possession).
        We use this to handle the initial random spawn.
        """
        if hasattr(self.db, 'needs_initial_spawn') and self.db.needs_initial_spawn:
            initial_message = "你在一片陌生的森林中醒来，四周弥漫着潮湿的泥土气息..."
            fallback_message = "你在一片虚无中醒来，周围什么都没有...（初始出生点未找到）"
            
            self._find_and_move_to_spawn_point(initial_message, fallback_message)
            
            # Remove the flag so it doesn't happen again
            if hasattr(self, "attributes") and self.attributes.has("needs_initial_spawn"):
                self.attributes.remove("needs_initial_spawn")
            elif hasattr(self.db, 'needs_initial_spawn'): 
                 del self.db.needs_initial_spawn


    def at_damage(self, amount, attacker=None):
        """
        Called when the character takes damage.
        """
        self.db.current_hp -= amount
        if attacker:
            self.msg(f"你受到了来自 {attacker.key} 的 {amount} 点伤害！")
        else:
            self.msg(f"你受到了 {amount} 点伤害！")

        if self.db.current_hp <= 0:
            self.at_death(killer=attacker)

    def at_death(self, killer=None):
        """
        Called when the character's HP drops to 0 or below.
        Now respawns in a random forest location.
        """
        death_message_self = ""
        death_message_others = ""

        if killer:
            death_message_self = f"你被 {killer.key} 杀死了！"
            death_message_others = f"{self.key} 被 {killer.key} 杀死了。"
        else:
            death_message_self = "你死了！"
            death_message_others = f"{self.key} 死了。"
        
        self.msg(death_message_self) # Send death message to self
        if self.location:
            self.location.msg_contents(death_message_others, exclude=self) # Send death message to others in room

        # Reset combat state and HP
        self.db.current_hp = self.db.max_hp 
        self.db.is_in_combat = False
        self.db.combat_target = None
        
        logger.log_infomsg(f"Character {self.key} died. Attempting respawn in forest.")

        # Respawn messages
        respawn_message = "你在森林的另一处苏醒过来，阳光透过树叶洒在你脸上，带来了些许暖意。"
        respawn_fallback_message = "你在朦胧中醒来，发现自己身处一个意想不到的地方...（复活点未找到）"

        self._find_and_move_to_spawn_point(respawn_message, respawn_fallback_message)
