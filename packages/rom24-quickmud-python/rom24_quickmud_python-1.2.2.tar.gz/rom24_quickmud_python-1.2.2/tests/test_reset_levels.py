from mud.world import initialize_world
from mud.registry import room_registry, area_registry, mob_registry, obj_registry
from mud.models.room_json import ResetJson


def setup_function(_):
    room_registry.clear(); area_registry.clear(); mob_registry.clear(); obj_registry.clear()


def test_give_equip_object_levels_are_in_expected_ranges(monkeypatch):
    from mud.utils import rng_mm
    initialize_world('area/area.lst')
    room = room_registry[3001]
    area = room.area; assert area is not None
    area.resets = []
    # Spawn a non-shopkeeper mob (604 in Midgaard is blacksmith, but use 6000 from haon? We'll use a generic mob present in registries)
    # Use 6004 (a deer) from haon isn't loaded by default; instead use 3003 (Janitor) present in Midgaard
    area.resets.append(ResetJson(command='M', arg2=3003, arg4=room.vnum))
    # Equip a weapon (object 3022: a short sword) with limit 1
    # Some legacy prototypes may lack type; set explicit types for the test
    from mud.registry import obj_registry
    obj_registry[3022].item_type = 5  # ItemType.WEAPON
    area.resets.append(ResetJson(command='E', arg2=3022, arg3=1, arg4=16))
    # Give an armor (object 3021: a small buckler)
    obj_registry[3021].item_type = 9  # ItemType.ARMOR
    area.resets.append(ResetJson(command='G', arg2=3021, arg3=1))

    # Make RNG deterministic for levels
    monkeypatch.setattr(rng_mm, 'number_range', lambda a, b: (a + b) // 2)
    from mud.spawning.reset_handler import apply_resets
    apply_resets(area)

    mob = next(p for p in room.people if getattr(getattr(p, 'prototype', None), 'vnum', None) == 3003)
    levels = [getattr(o, 'level', 0) for o in getattr(mob, 'inventory', [])]
    assert any(5 <= lvl <= 15 for lvl in levels), 'weapon/armor levels within expected ranges'
