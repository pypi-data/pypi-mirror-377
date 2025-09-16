from mcshell.constants import *

def make_picker_group(materials,reg_exp):
    _matches = list(filter(lambda x: x is not None, map(lambda x:re.match(reg_exp,x),set(materials))))
    return [_m.group() for _m in _matches]

# Define the patterns and groups for categorization
# This is the primary place to configure how materials are grouped
COLORABLE_BASE_RULES = {
    # Key: The base name for the blockly block (e.g., 'WOOL')
    # Value: A regex pattern to identify variants. The pattern MUST have one
    #        capturing group for the color part of the name.
    'WOOL': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_WOOL$"),
    'TERRACOTTA': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK|LIGHT|LEGACY)_TERRACOTTA$"),
    'STAINED_GLASS': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_STAINED_GLASS$"),
    'STAINED_GLASS_PANE': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_STAINED_GLASS_PANE$"),
    'CONCRETE': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CONCRETE$"),
    'CONCRETE_POWDER': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CONCRETE_POWDER$"),
    'CANDLE': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CANDLE$"),
    'BED': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_BED$"),
    'BANNER': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_(WALL_)?BANNER$"),
    'SHULKER_BOX': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_SHULKER_BOX$"),
    'CARPET': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_CARPET$"),
    'GLAZED_TERRACOTTA': re.compile(r"^(WHITE|ORANGE|MAGENTA|LIGHT_BLUE|YELLOW|LIME|PINK|GRAY|LIGHT_GRAY|CYAN|PURPLE|BLUE|BROWN|GREEN|RED|BLACK)_GLAZED_TERRACOTTA$"),
}

# Define the contents of each picker block you want to generate
MATERIAL_PICKER_GROUPS = {
    "world": ["AIR", "STONE", "GRANITE", "DIORITE", "ANDESITE", "DEEPSLATE", "CALCITE", "TUFF", "DIRT", "COARSE_DIRT", "ROOTED_DIRT", "GRASS_BLOCK", "PODZOL", "MYCELIUM", "DIRT_PATH", "SAND", "RED_SAND", "GRAVEL", "CLAY", "ICE", "PACKED_ICE", "BLUE_ICE", "SNOW", "SNOW_BLOCK", "WATER", "LAVA", "BEDROCK", "OBSIDIAN", "CRYING_OBSIDIAN", "MAGMA_BLOCK"],
    "ores": ["COAL_ORE", "DEEPSLATE_COAL_ORE", "IRON_ORE", "DEEPSLATE_IRON_ORE", "COPPER_ORE", "DEEPSLATE_COPPER_ORE", "GOLD_ORE", "DEEPSLATE_GOLD_ORE", "REDSTONE_ORE", "DEEPSLATE_REDSTONE_ORE", "EMERALD_ORE", "DEEPSLATE_EMERALD_ORE", "LAPIS_ORE", "DEEPSLATE_LAPIS_ORE", "DIAMOND_ORE", "DEEPSLATE_DIAMOND_ORE", "NETHER_GOLD_ORE", "NETHER_QUARTZ_ORE", "ANCIENT_DEBRIS"],
    "wood_planks": ["OAK_PLANKS", "SPRUCE_PLANKS", "BIRCH_PLANKS", "JUNGLE_PLANKS", "ACACIA_PLANKS", "DARK_OAK_PLANKS", "MANGROVE_PLANKS", "CHERRY_PLANKS", "BAMBOO_PLANKS", "CRIMSON_PLANKS", "WARPED_PLANKS", "BAMBOO_MOSAIC"],
    "wood_logs": ["OAK_LOG", "SPRUCE_LOG", "BIRCH_LOG", "JUNGLE_LOG", "ACACIA_LOG", "DARK_OAK_LOG", "MANGROVE_LOG", "CHERRY_LOG", "CRIMSON_STEM", "WARPED_STEM", "STRIPPED_OAK_LOG", "STRIPPED_SPRUCE_LOG", "STRIPPED_BIRCH_LOG", "STRIPPED_JUNGLE_LOG", "STRIPPED_ACACIA_LOG", "STRIPPED_DARK_OAK_LOG", "STRIPPED_MANGROVE_LOG", "STRIPPED_CHERRY_LOG", "STRIPPED_CRIMSON_STEM", "STRIPPED_WARPED_STEM"],
    "wood_full": ["OAK_WOOD", "SPRUCE_WOOD", "BIRCH_WOOD", "JUNGLE_WOOD", "ACACIA_WOOD", "DARK_OAK_WOOD", "MANGROVE_WOOD", "CHERRY_WOOD", "CRIMSON_HYPHAE", "WARPED_HYPHAE", "STRIPPED_OAK_WOOD", "STRIPPED_SPRUCE_WOOD", "STRIPPED_BIRCH_WOOD", "STRIPPED_JUNGLE_WOOD", "STRIPPED_ACACIA_WOOD", "STRIPPED_DARK_OAK_WOOD", "STRIPPED_MANGROVE_WOOD", "STRIPPED_CHERRY_WOOD", "STRIPPED_CRIMSON_HYPHAE", "STRIPPED_WARPED_HYPHAE", "BAMBOO_BLOCK", "STRIPPED_BAMBOO_BLOCK"],
    "stone_bricks": ["BRICKS", "STONE_BRICKS", "MUD_BRICKS", "DEEPSLATE_BRICKS", "DEEPSLATE_TILES", "NETHER_BRICKS", "RED_NETHER_BRICKS", "POLISHED_BLACKSTONE_BRICKS", "END_STONE_BRICKS", "QUARTZ_BRICKS", "CHISELED_STONE_BRICKS", "CRACKED_STONE_BRICKS", "MOSSY_STONE_BRICKS", "CHISELED_NETHER_BRICKS", "CRACKED_NETHER_BRICKS", "CHISELED_POLISHED_BLACKSTONE", "CRACKED_POLISHED_BLACKSTONE_BRICKS", "CHISELED_DEEPSLATE", "CRACKED_DEEPSLATE_BRICKS", "CRACKED_DEEPSLATE_TILES", "CHISELED_TUFF_BRICKS"],
    "glass": ["GLASS", "GLASS_PANE", "TINTED_GLASS"],
    "redstone_components": ["REDSTONE_WIRE", "REDSTONE_BLOCK", "REDSTONE_TORCH", "REPEATER", "COMPARATOR", "PISTON", "STICKY_PISTON", "SLIME_BLOCK", "HONEY_BLOCK", "OBSERVER", "DROPPER", "DISPENSER", "HOPPER", "LECTERN", "LEVER", "DAYLIGHT_DETECTOR", "TRIPWIRE_HOOK", "TARGET", "NOTE_BLOCK", "RAIL", "POWERED_RAIL", "DETECTOR_RAIL", "ACTIVATOR_RAIL", "REDSTONE_LAMP"],
    # Add more groups as needed (stairs, slabs, fences, doors, etc.)
}

def process_materials():
    """
    Reads the full material list and categorizes materials into
    colorable bases, specific picker groups, and single/misc items.
    """
    try:
        _raw_materials_list = pickle.load(MC_MATERIALS_PATH.open('rb'))
    except FileNotFoundError:
        from mcshell.mcscraper import make_materials
        _raw_materials_list = make_materials()

    all_materials = set()
    for mat in _raw_materials_list:
        if mat and not mat.startswith("LEGACY_"):  # Ignore legacy materials
            all_materials.add(mat)

    MATERIAL_PICKER_GROUPS['stairs'] = make_picker_group(all_materials, r".*_STAIRS$")
    MATERIAL_PICKER_GROUPS['slabs'] = make_picker_group(all_materials, r".*_SLAB$")
    MATERIAL_PICKER_GROUPS['fences'] = make_picker_group(all_materials, r".*_FENCE$")
    MATERIAL_PICKER_GROUPS['gates'] = make_picker_group(all_materials, r".*_GATE$")
    MATERIAL_PICKER_GROUPS['doors'] = make_picker_group(all_materials, r".*_DOOR$")
    MATERIAL_PICKER_GROUPS['trapdoors'] = make_picker_group(all_materials, r".*_TRAPDOOR$")
    MATERIAL_PICKER_GROUPS['walls'] = make_picker_group(all_materials, r".*_WALL$")

    colorable_bases = {}  # e.g., {'WOOL': ['WHITE_WOOL', 'BLUE_WOOL', ...]}
    picker_data = {}      # e.g., {'ores': ['COAL_ORE', 'IRON_ORE', ...]}
    processed_materials = set()

    # 1. Identify and categorize colorable materials
    for base_name, pattern in COLORABLE_BASE_RULES.items():
        colorable_bases[base_name] = []
        for mat in list(all_materials):
            if pattern.match(mat):
                colorable_bases[base_name].append(mat)
                processed_materials.add(mat)

    # 2. Identify materials for specific picker groups
    for group_name, material_list in MATERIAL_PICKER_GROUPS.items():
        picker_data[group_name] = []
        for mat_id in material_list:
            if mat_id in all_materials:
                picker_data[group_name].append(mat_id)
                processed_materials.add(mat_id)

    # 3. All remaining materials are singles/miscellaneous
    singles_data = sorted(list(all_materials - processed_materials))


    try:
        # colorable, pickers, singles = process_materials()

        with MC_COLOURABLE_MATERIALS_DATA_PATH.open('w') as f:
            json.dump(colorable_bases, f, indent=4, sort_keys=True)
        # print("Successfully generated colourables.json")

        with MC_PICKER_MATERIALS_DATA_PATH.open('w') as f:
            json.dump(picker_data, f, indent=4,sort_keys=True)
        # print("Successfully generated pickers.json")

        with MC_SINGLE_MATERIALS_DATA_PATH.open('w') as f:
            json.dump(singles_data, f, indent=4, sort_keys=True)
        # print("Successfully generated singles.json")
    except Exception as e:
        print(f"An error occurred: {e}")
    # finally:
    #     return colorable_bases, picker_data, singles_data


# Define the groups for entity picker blocks. The key will be the picker name
# (e.g., 'hostile_mobs') and the value is a list of entity IDs to include.
# You can customize these groups as you see fit.
ENTITY_PICKER_GROUPS = {
    "boats": [
        "ACACIA_BOAT", "BAMBOO_RAFT", "BIRCH_BOAT", "CHERRY_BOAT", "DARK_OAK_BOAT",
        "JUNGLE_BOAT", "MANGROVE_BOAT", "OAK_BOAT", "SPRUCE_BOAT", "PALE_OAK_BOAT"
    ],
    "chest_boats": [
        "ACACIA_CHEST_BOAT", "BAMBOO_CHEST_RAFT", "BIRCH_CHEST_BOAT", "CHERRY_CHEST_BOAT",
        "DARK_OAK_CHEST_BOAT", "JUNGLE_CHEST_BOAT", "MANGROVE_CHEST_BOAT", "OAK_CHEST_BOAT",
        "SPRUCE_CHEST_BOAT", "PALE_OAK_CHEST_BOAT"
    ],
    "minecarts": [
        "MINECART", "CHEST_MINECART", "COMMAND_BLOCK_MINECART", "FURNACE_MINECART",
        "HOPPER_MINECART", "SPAWNER_MINECART", "TNT_MINECART"
    ],
    "passive_mobs": [
        "ALLAY", "ARMADILLO", "AXOLOTL", "BAT", "CAMEL", "CAT", "CHICKEN", "COD", "COW",
        "DONKEY", "FOX", "FROG", "GLOW_SQUID", "HORSE", "MOOSHROOM", "MULE", "OCELOT",
        "PANDA", "PARROT", "PIG", "POLAR_BEAR", "PUFFERFISH", "RABBIT", "SALMON",
        "SHEEP", "SNIFFER", "SQUID", "STRIDER", "TADPOLE", "TROPICAL_FISH", "TURTLE",
        "VILLAGER", "WANDERING_TRADER", "WOLF"
    ],
    "hostile_mobs": [
        "BLAZE", "BOGGED", "BREEZE", "CAVE_SPIDER", "CREAKING", "CREEPER", "DROWNED",
        "ELDER_GUARDIAN", "ENDERMAN", "ENDERMITE", "EVOKER", "GHAST", "GUARDIAN",
        "HOGLIN", "HUSK", "ILLUSIONER", "MAGMA_CUBE", "PHANTOM", "PIGLIN",
        "PIGLIN_BRUTE", "PILLAGER", "RAVAGER", "SHULKER", "SILVERFISH", "SKELETON",
        "SLIME", "SPIDER", "STRAY", "VEX", "VINDICATOR", "WARDEN", "WITCH", "WITHER",
        "WITHER_SKELETON", "ZOGLIN", "ZOMBIE", "ZOMBIE_VILLAGER", "ZOMBIFIED_PIGLIN"
    ],
    "projectiles": [
        "ARROW", "BREEZE_WIND_CHARGE", "DRAGON_FIREBALL", "EGG", "ENDER_PEARL",
        "EXPERIENCE_BOTTLE", "FIREBALL", "FIREWORK_ROCKET", "FISHING_BOBBER",
        "LLAMA_SPIT", "SHULKER_BULLET", "SMALL_FIREBALL", "SNOWBALL",
        "SPECTRAL_ARROW", "SPLASH_POTION", "LINGERING_POTION", "TRIDENT", "WIND_CHARGE", "WITHER_SKULL"
    ],
    "utility_and_special": [
        "AREA_EFFECT_CLOUD", "ARMOR_STAND", "BLOCK_DISPLAY", "END_CRYSTAL",
        "EXPERIENCE_ORB", "EYE_OF_ENDER", "FALLING_BLOCK", "GLOW_ITEM_FRAME",
        "INTERACTION", "ITEM", "ITEM_DISPLAY", "ITEM_FRAME", "LEASH_KNOT",
        "LIGHTNING_BOLT", "MARKER", "OMINOUS_ITEM_SPAWNER", "PAINTING", "PLAYER",
        "TEXT_DISPLAY"
    ]
    # Note: Spawn eggs are typically items, not placeable entities, so they are omitted here.
    # You could create a separate "spawn_eggs" picker if needed.
}

def process_entities(filepath="entity-list.txt"):
    """
    Reads the full entity list and categorizes them into picker groups.
    """

    try:
        _raw_entity_id_map = pickle.load(MC_ENTITY_ID_MAP_PATH.open('rb'))
    except FileNotFoundError:
        from mcshell.mcscraper import make_entity_id_map
        _raw_entity_id_map = make_entity_id_map()

    all_entities = set()
    for _ent,_id in _raw_entity_id_map.items():
        if not _ent.startswith("LEGACY_"):  # Ignore legacy materials
            all_entities.add(_ent)

    picker_data = {}
    processed_entities = set()

    # Populate picker groups from the defined lists
    for group_name, entity_list in ENTITY_PICKER_GROUPS.items():
        picker_data[group_name] = []
        for entity_id in entity_list:
            if entity_id in all_entities:
                picker_data[group_name].append(entity_id)
                processed_entities.add(entity_id)
            else:
                print(f"Warning: Entity ID '{entity_id}' listed in group '{group_name}' not found in master list.")
        if not picker_data[group_name]:
            picker_data.pop(group_name)

    # All remaining entities go into a miscellaneous group
    misc_entities = sorted(list(all_entities - processed_entities))
    if misc_entities:
        picker_data["miscellaneous_entities"] = misc_entities

    try:
        with MC_ENTITY_PICKERS_PATH.open('w') as f:
            json.dump(picker_data, f, indent=4, sort_keys=True)
        # print("Successfully generated pickers.json")
    except Exception as e:
        print(f"An error occurred: {e}")

def _generate_blockly_name(id_string):
    """Helper to format names like HOSTILE_MOBS -> 'Hostile Mobs'."""
    if not id_string or not isinstance(id_string, str):
        return ''
    return id_string.replace('_', ' ').title()

def generate_entity_blocks():
    """
    Generates Blockly definitions, Python generators, and a toolbox.xml file
    for Minecraft entities, correctly processing the pickers.json format.
    """
    try:
        # --- 1. Set up paths ---
        entities_data_dir = MC_DATA_DIR / 'entities'
        pickers_path = entities_data_dir / 'pickers.json'

        output_blocks_dir = MC_APP_SRC_DIR / 'blocks'
        output_python_dir = MC_APP_SRC_DIR / 'generators' / 'python'
        output_toolbox_path = MC_APP_SRC_DIR / 'toolbox.xml'

        # --- 2. Load data ---
        with open(pickers_path, 'r', encoding='utf-8') as f:
            pickers_data = json.load(f)

        # --- 3. Initialize outputs ---
        block_defs_list = []
        python_gen_list = []
        toolbox_xml_categories = []

        # Default values, since they aren't in the new pickers.json
        default_colour = "#5b5ba5"

        # --- 4. Process each picker and generate code ---
        # CORRECTED: Iterate over the dictionary items directly.
        for name, entities in pickers_data.items():
            blockly_name = _generate_blockly_name(name)
            block_type = f"minecraft_entity_picker_{name.lower()}"
            tooltip = f"Select a {blockly_name.lower()} entity."

            # a. Generate Toolbox XML category.
            # In the original JS, it seems it created individual blocks, not categories.
            # Let's create a single category for entities with all picker blocks inside.
            toolbox_xml_categories.append(f'  <block type="{block_type}"></block>')

            # b. Generate the picker block with the dropdown.
            dropdown_options = ',\n'.join([
                f'          ["{_generate_blockly_name(entity)}", "{entity}"]'
                for entity in entities
            ])

            block_defs_list.append(f"""
    Blockly.Blocks['{block_type}'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("{blockly_name}")
            .appendField(new Blockly.FieldDropdown([
    {dropdown_options}
            ]), "ENTITY_ID");
        this.setOutput(true, "Entity");
        this.setColour("{default_colour}");
        this.setTooltip("{tooltip}");
        this.setHelpUrl("");
      }}
    }};""")

            python_gen_list.append(f"""
    pythonGenerator.forBlock['{block_type}'] = function(block, generator) {{
      const dropdown_entity = block.getFieldValue('ENTITY_ID');
      const code = `'${{dropdown_entity}}'`;
      return [code, generator.ORDER_ATOMIC];
    }};""")

        # --- 5. Assemble final output strings ---
        block_defs_output = "export function defineMineCraftEntityBlocks(Blockly) {\n" + \
                            "\n".join(block_defs_list) + "\n}\n"

        python_gen_output = "export function defineMineCraftEntityGenerators(pythonGenerator) {\n" + \
                            "\n".join(python_gen_list) + "\n}\n"

        _newline = "\n"
        # Create a single "Entities" category in the toolbox
        toolbox_xml_output = f"""<category name="Entities" colour="{default_colour}">
{
_newline.join(toolbox_xml_categories)
}
</category>"""

        # --- 6. Write to files ---
        output_blocks_dir.mkdir(parents=True, exist_ok=True)
        output_python_dir.mkdir(parents=True, exist_ok=True)

        (output_blocks_dir / 'entities.mjs').write_text(block_defs_output, 'utf-8')
        print("Successfully generated blocks/entities.mjs")

        (output_python_dir / 'entities.mjs').write_text(python_gen_output, 'utf-8')
        print("Successfully generated python/entities.mjs")

        from blockapily import BlocklyGenerator
        BlocklyGenerator.update_toolbox(toolbox_xml_output, output_toolbox_path)
        print(f"Successfully updated {output_toolbox_path}")

    except Exception as e:
        print(f"Failed to generate entity Blockly files: {e}")
        raise

def generate_material_blocks():
    """
    A precise Python translation of the original generate_material_blocks.mjs.
    This version correctly generates the toolbox.xml with a single category
    and proper shadow blocks.
    """
    try:
        # --- 1. Set up paths ---
        materials_data_dir = MC_DATA_DIR / 'materials'

        colourables_path = materials_data_dir / 'colourables.json'
        pickers_path = materials_data_dir / 'pickers.json'
        singles_path = materials_data_dir / 'singles.json'

        output_blocks_dir = MC_APP_SRC_DIR / 'blocks'
        output_python_dir = MC_APP_SRC_DIR / 'generators' / 'python'
        output_toolbox_path = MC_APP_SRC_DIR / 'toolbox.xml'

        # --- 2. Load all data files ---
        with open(colourables_path, 'r', encoding='utf-8') as f:
            colourables_data = json.load(f)
        with open(pickers_path, 'r', encoding='utf-8') as f:
            pickers_data = json.load(f)
        with open(singles_path, 'r', encoding='utf-8') as f:
            singles_data = json.load(f)

        # --- 3. Initialize outputs ---
        block_defs_list = []
        python_gen_list = []
        toolbox_xml_blocks = [] # List to hold all <block> and <sep> entries
        default_colour = 160
        picker_colour = 180
        misc_colour = 200

        # --- 4. Process data and generate code ---

        # A. Process Colourable Blocks (e.g., "BANNER")
        for name in colourables_data:
            block_type = f"minecraft_material_{name.lower()}"
            tooltip = f"A {_generate_blockly_name(name)} block that can be colored."

            # CORRECTED TOOLBOX LOGIC: Add a block with a shadow definition
            toolbox_xml_blocks.append(f"""    <block type="{block_type}">
      <value name="COLOUR">
        <shadow type="minecraft_coloured_block_picker">
          <field name="MINECRAFT_COLOUR_ID">WHITE</field>
        </shadow>
      </value>
    </block>""")

            block_defs_list.append(f"""
    Blockly.Blocks['{block_type}'] = {{
      init: function() {{
        this.appendValueInput("COLOUR")
            .setCheck("MinecraftColour")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("{name} with color");
        this.setOutput(true, "Block");
        this.setColour({default_colour});
        this.setTooltip("{tooltip}");
        MCED.Defaults.values['{block_type}'] = {{
          COLOUR: {{ shadow: '<shadow type="minecraft_coloured_block_picker"><field name="MINECRAFT_COLOUR_ID">WHITE</field></shadow>' }}
        }};
        MCED.BlocklyUtils.configureShadow(this, "COLOUR");
      }}
    }};""")
            python_gen_list.append(f"""
    pythonGenerator.forBlock['{block_type}'] = function(block, generator) {{
      const colour = generator.valueToCode(block, 'COLOUR', generator.ORDER_ATOMIC) || "'WHITE'";
      const code = _combine_colour_and_material(`'${{colour}}'`, '{name}');
      return [code, generator.ORDER_ATOMIC];
    }};""")

        # B. Process Picker Blocks (e.g., "walls")
        for name, materials in pickers_data.items():
            block_type = f"minecraft_picker_{name.lower()}"
            toolbox_xml_blocks.append(f'    <block type="{block_type}"></block>')
            dropdown_options = ',\n'.join([f'                ["{_generate_blockly_name(mat)}", "{mat}"]' for mat in materials])
            block_defs_list.append(f"""
    Blockly.Blocks['{block_type}'] = {{
        init: function() {{
            this.appendDummyInput()
                .appendField("{_generate_blockly_name(name)}")
                .appendField(new Blockly.FieldDropdown([
    {dropdown_options}
                ]), "MATERIAL_ID");
            this.setOutput(true, "Block");
            this.setColour({picker_colour});
            this.setTooltip("Select a {_generate_blockly_name(name)} material.");
        }}
    }};""")
            python_gen_list.append(f"""
    pythonGenerator.forBlock['{block_type}'] = function(block, generator) {{
      const material_id = block.getFieldValue('MATERIAL_ID');
      return [`'${{material_id}}'`, generator.ORDER_ATOMIC];
    }};""")

        # C. Process Single Blocks into one "Miscellaneous" Picker
        if singles_data:
            block_type = "minecraft_picker_miscellaneous"
            toolbox_xml_blocks.append('    <sep></sep>')
            toolbox_xml_blocks.append(f'    <block type="{block_type}"></block>')
            dropdown_options = ',\n'.join([f'                ["{_generate_blockly_name(mat)}", "{mat}"]' for mat in singles_data])
            block_defs_list.append(f"""
    Blockly.Blocks['{block_type}'] = {{
        init: function() {{
            this.appendDummyInput()
                .appendField("Misc. Block/Item")
                .appendField(new Blockly.FieldDropdown([
    {dropdown_options}
                ]), "MATERIAL_ID");
            this.setOutput(true, "Block");
            this.setColour({misc_colour});
            this.setTooltip("Select a miscellaneous Minecraft block or item.");
        }}
    }};""")
            python_gen_list.append(f"""
    pythonGenerator.forBlock['{block_type}'] = function(block, generator) {{
      const material_id = block.getFieldValue('MATERIAL_ID');
      return [`'${{material_id}}'`, generator.ORDER_ATOMIC];
    }};""")

        # --- 5. Assemble and write final output files ---
            block_defs_output = 'import { MCED } from "../lib/constants.mjs";\n\n' + \
                            "export function defineMineCraftMaterialBlocks(Blockly) {\n" + \
                            "\n".join(block_defs_list) + "\n}\n"
        python_helper = """
function _combine_colour_and_material(colour, material) {
    const cleanColour = colour.replace(/['"]/g, '');
    return `'${cleanColour}_${material}'`;
}"""
        python_gen_output = "import { pythonGenerator } from 'blockly/python';\n" + \
                            python_helper + \
                            "\n\nexport function defineMineCraftMaterialGenerators(pythonGenerator) {\n" + \
                            "\n".join(python_gen_list) + "\n}\n"

        # CORRECTED TOOLBOX ASSEMBLY: Create a single category containing all blocks
        toolbox_xml_output = f"""<category name="Materials" colour="#777777">
{''.join(toolbox_xml_blocks)}
</category>"""

        # --- 6. Write to files ---
        output_blocks_dir.mkdir(parents=True, exist_ok=True)
        output_python_dir.mkdir(parents=True, exist_ok=True)

        (output_blocks_dir / 'materials.mjs').write_text(block_defs_output, 'utf-8')
        print("Successfully generated blocks/materials.mjs")
        (output_python_dir / 'materials.mjs').write_text(python_gen_output, 'utf-8')
        print("Successfully generated python/materials.mjs")

        BlocklyGenerator.update_toolbox(toolbox_xml_output, output_toolbox_path)
        print(f"Successfully updated {output_toolbox_path}")

    except Exception as e:
        print(f"Failed to generate material Blockly files: {e}")
        raise

def generate_mcactions_blocks():

    _type_map = {
        'Vec3': "3DVector", 'Matrix3': "3DMatrix", 'Block': "Block"
    }

    _shadow_map = dict(
        Vec3='''
                 <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>   
        ''',
        Block='''
                <shadow type="minecraft_picker_world">
                    <field name="MATERIAL_ID">STONE</field>
                </shadow>
        ''',
        Entity='''
                <shadow type="minecraft_entity_picker_passive_mobs">
                    <field name="ENTITY_ID">PIG</field>
                </shadow>
        ''',
        Matrx3='''
                <shadow type="minecraft_matrix_3d_euler"></shadow>
        '''

    )

    output_blocks_dir = MC_APP_SRC_DIR / 'blocks'
    output_python_dir = MC_APP_SRC_DIR / 'generators' / 'python'
    output_toolbox_path = MC_APP_SRC_DIR / 'toolbox.xml'

    from mcshell.mcactions import MCActions
    for _api_class in MCActions.__bases__:
        _block_output_path = output_blocks_dir / f'{_api_class.__name__}.mjs'
        _gens_output_path = output_python_dir / f'{_api_class.__name__}.mjs'


        _block_output = '\nimport { MCED } from "../lib/constants.mjs";' + f"\nexport function define{_api_class.__name__}Blocks(Blockly) " + "{\n"
        _gens_output = f"\n\nexport function define{_api_class.__name__}Generators(pythonGenerator) " + "{\n"

        _blks, _gens, _cat = BlocklyGenerator(_api_class, _type_map, _shadow_map).generate()
        _block_output += _blks + "\n"
        _gens_output += _gens + "\n"

        _block_output_path.write_text(_block_output + "\n}", 'utf-8')
        _gens_output_path.write_text(_gens_output + "\n}", 'utf-8')

        print(f"Successfully generated {_block_output_path}")
        print(f"Successfully generated {_gens_output_path}")

        BlocklyGenerator.update_toolbox(_cat, output_toolbox_path)
        print(f"Successfully updated {output_toolbox_path}")

#