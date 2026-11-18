'use strict'
// What Jenbina can perceive right now, as plain data for the Python side.

const { hasSameOrBetterTool } = require('./words')

const ANIMALS = new Set(['cow', 'pig', 'sheep', 'chicken', 'rabbit', 'mooshroom'])
const HOSTILES = new Set([
  'zombie', 'skeleton', 'creeper', 'spider', 'cave_spider', 'enderman', 'witch',
  'drowned', 'husk', 'stray', 'phantom', 'slime', 'zombie_villager', 'pillager'
])
// Best first: what she reaches for when she eats.
const FOODS = [
  'cooked_beef', 'cooked_porkchop', 'cooked_mutton', 'cooked_chicken', 'cooked_rabbit',
  'bread', 'baked_potato', 'apple', 'carrot', 'beef', 'porkchop', 'mutton', 'rabbit',
  'sweet_berries', 'melon_slice', 'potato', 'chicken', 'rotten_flesh'
]
const CRAFT_WHITELIST = [
  'planks', 'stick', 'crafting_table',
  'wooden_pickaxe', 'wooden_axe', 'wooden_sword',
  'stone_pickaxe', 'stone_axe', 'stone_sword', 'furnace'
]
const STONE_BLOCKS = ['stone', 'cobblestone', 'andesite', 'diorite', 'granite']
const SIDES = [[1, 0], [-1, 0], [0, 1], [0, -1]]

const SIGHT = 32
const REACH = 4

function inventoryCounts (bot) {
  const counts = {}
  for (const item of bot.inventory.items()) counts[item.name] = (counts[item.name] || 0) + item.count
  return counts
}

function blockIds (bot, names) {
  return names.map(name => bot.registry.blocksByName[name]).filter(Boolean).map(block => block.id)
}

function logIds (bot) {
  return Object.values(bot.registry.blocksByName).filter(b => b.name.endsWith('_log')).map(b => b.id)
}

function isSolid (bot, position) {
  const block = bot.blockAt(position)
  return !!block && block.boundingBox === 'block'
}

/** Enclosed on all four sides at feet and head height, with a roof overhead. */
function isSheltered (bot) {
  const feet = bot.entity.position.floored()
  if (!isSolid(bot, feet.offset(0, 2, 0))) return false
  return SIDES.every(([dx, dz]) =>
    isSolid(bot, feet.offset(dx, 0, dz)) && isSolid(bot, feet.offset(dx, 1, dz)))
}

function tableWithinReach (bot) {
  return bot.findBlock({ matching: blockIds(bot, ['crafting_table']), maxDistance: REACH })
}

/** Whitelisted items she could make now and does not already have enough of. */
function craftable (bot) {
  const inventory = inventoryCounts(bot)
  const has = name => (inventory[name] || 0) > 0
  const tableAvailable = !!tableWithinReach(bot) || has('crafting_table')
  const names = []
  if (Object.keys(inventory).some(name => name.endsWith('_log'))) names.push('planks')
  for (const name of CRAFT_WHITELIST) {
    if (name === 'planks') continue
    if (name === 'crafting_table' && tableAvailable) continue
    if (name === 'stick' && (inventory.stick || 0) >= 4) continue
    if (name === 'furnace' && has('furnace')) continue
    if (hasSameOrBetterTool(inventory, name)) continue
    const item = bot.registry.itemsByName[name]
    if (item && bot.recipesFor(item.id, null, 1, tableAvailable ? true : null).length > 0) names.push(name)
  }
  return names
}

function nearbyCreatures (bot, names, range) {
  const here = bot.entity.position
  return Object.values(bot.entities)
    .filter(e => e !== bot.entity && names.has(e.name) && e.position.distanceTo(here) <= range)
    .map(e => ({ name: e.name, distance: Math.round(e.position.distanceTo(here)) }))
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 5)
}

/** Biome name and Minecraft temperature (0.8 is plains) where she stands. */
function biomeAt (bot, position) {
  // On 1.21 the block's own biome has no name; the server's registry does.
  try {
    const biome = bot.registry.biomes[bot.world.getBiome(position)]
    if (biome && biome.name) {
      return { name: biome.name, temperature: Number.isFinite(biome.temperature) ? biome.temperature : null }
    }
  } catch (e) {}
  return { name: 'unknown', temperature: null }
}

function observe (bot) {
  const position = bot.entity.position.floored()
  const biome = biomeAt(bot, position)
  const timeOfDay = bot.time.timeOfDay
  return {
    position: { x: position.x, y: position.y, z: position.z },
    biome: biome.name,
    temperature: biome.temperature,
    sky: {
      is_day: timeOfDay < 12542 || timeOfDay > 23460,
      time_of_day: timeOfDay,
      raining: !!bot.isRaining
    },
    health: Math.round(bot.health ?? 20),
    food: Math.round(bot.food ?? 20),
    inventory: inventoryCounts(bot),
    nearby: {
      logs: bot.findBlocks({ matching: logIds(bot), maxDistance: SIGHT, count: 20 }).length,
      stone: !!bot.findBlock({ matching: blockIds(bot, STONE_BLOCKS), maxDistance: 16 }),
      water: !!bot.findBlock({ matching: blockIds(bot, ['water']), maxDistance: 16 }),
      animals: nearbyCreatures(bot, ANIMALS, SIGHT),
      hostiles: nearbyCreatures(bot, HOSTILES, 24),
      crafting_table: !!tableWithinReach(bot)
    },
    craftable: craftable(bot),
    sheltered: isSheltered(bot)
  }
}

module.exports = {
  ANIMALS,
  CRAFT_WHITELIST,
  FOODS,
  REACH,
  SIDES,
  SIGHT,
  STONE_BLOCKS,
  blockIds,
  inventoryCounts,
  isSheltered,
  isSolid,
  logIds,
  observe,
  tableWithinReach
}
