from evennia.scripts.scripts import DefaultScript
from evennia.utils import logger
import time # Import time for timestamping logs

class NeedsSystem(DefaultScript):
    """
    Manages the basic needs of characters, such as hunger, thirst, and temperature.
    This script is intended to be run globally and affect all PrimordialCharacters.
    """

    def at_script_creation(self):
        """
        Called when the script is first created.
        """
        self.key = "NeedsSystem_Global" # Default key if started via @script
        self.desc = "Manages character needs globally."
        # self.interval will be overridden by GLOBAL_SCRIPTS setting if started that way
        self.interval = 60  # Update needs every 60 seconds (1 minute)
        self.persistent = True # Persist this script through server reboots

    def at_repeat(self):
        """
        Called every `self.interval` seconds.
        This is where the main logic for updating needs will go.
        """
        logger.log_infomsg(f"NeedsSystem: at_repeat called at {time.time()}")
        # Import here to avoid circular dependencies at load time
        from typeclasses.characters import PrimordialCharacter

        characters = PrimordialCharacter.objects.all()
        online_characters = [char for char in characters if char.has_account and char.account.is_connected]
        
        logger.log_infomsg(f"NeedsSystem: Found {len(online_characters)} online PrimordialCharacters.")

        for char in online_characters:
            original_hunger = char.db.hunger
            logger.log_infomsg(f"NeedsSystem: Processing character {char.key} (ID: {char.id}). Current hunger: {original_hunger}")

            # --- Hunger --- 
            char.db.hunger = max(0, char.db.hunger - 1)
            logger.log_infomsg(f"NeedsSystem: Character {char.key} new hunger: {char.db.hunger}")
            
            if char.db.hunger <= 0:
                char.msg("你感到极度饥饿，胃里传来阵阵绞痛！")
                char.at_damage(1, attacker=None)
            elif char.db.hunger < 25:
                char.msg("你的肚子咕咕叫，你非常饿。")

            # --- Thirst ---
            original_thirst = char.db.thirst
            logger.log_infomsg(f"NeedsSystem: Character {char.key} current thirst: {original_thirst}")
            char.db.thirst = max(0, char.db.thirst - 2)
            logger.log_infomsg(f"NeedsSystem: Character {char.key} new thirst: {char.db.thirst}")

            if char.db.thirst <= 0:
                char.msg("你感到喉咙快要烧起来了，极度干渴！")
                char.at_damage(1, attacker=None)
            elif char.db.thirst < 25:
                char.msg("你口干舌燥，非常渴。")

            # --- Stamina/Energy ---
            original_stamina = char.db.stamina
            # Stamina regeneration
            if not char.db.is_in_combat and char.db.hunger > 10 and char.db.thirst > 10:
                char.db.stamina = min(100, char.db.stamina + 5)
            # Stamina drain from extreme conditions
            if char.db.hunger < 10 or char.db.thirst < 10:
                char.db.stamina = max(0, char.db.stamina - 2)
                if char.db.stamina == 0:
                    char.msg("你感到筋疲力尽，连动一根手指的力气都没有了。")
            if char.db.stamina != original_stamina: # Log only if changed
                 logger.log_infomsg(f"NeedsSystem: Character {char.key} new stamina: {char.db.stamina}")


            # --- Temperature (Simplified) ---
            original_temp = char.db.temperature
            current_temp_effect = -0.1 
            char.db.temperature += current_temp_effect
            char.db.temperature = round(char.db.temperature, 1)
            if char.db.temperature != original_temp: # Log only if changed
                logger.log_infomsg(f"NeedsSystem: Character {char.key} new temperature: {char.db.temperature}")


            if char.db.temperature < 35.0:
                char.msg("你感到非常寒冷，身体开始颤抖。")
                char.at_damage(1, attacker=None) # Take 1 damage from cold
            elif char.db.temperature < 36.0:
                char.msg("你觉得有点冷。")
            elif char.db.temperature > 38.5:
                char.msg("你觉得有些热得不舒服。")

    def at_start(self):
        """
        Called when the script is started or the server reloads.
        """
        # Log the interval the script believes it's running at.
        logger.log_infomsg(f"NeedsSystem (ID: {self.id}, DBRef: {self.dbref}, Key: {self.key}) started. Interval: {self.interval}s. Persistent: {self.persistent}.")

    def at_stop(self):
        """
        Called when the script is stopped or the server unloads it.
        """
        logger.log_infomsg(f"NeedsSystem (ID: {self.id}, DBRef: {self.dbref}, Key: {self.key}) stopped.")
