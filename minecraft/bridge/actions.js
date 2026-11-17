'use strict'
// The bounded routines Jenbina can perform. Each takes (bot, args, ctx) and
// returns { ok, sentence }. `ctx.deadline` is the wall-clock time by which the
// routine must have returned; loops check it and every step has its own limit.

const { goals } = require('mineflayer-pathfinder')
const { Vec3 } = require('vec3')
const { DIRECTIONS, bestTool } = require('./words')
const {
  ANIMALS, CRAFT_WHITELIST, FOODS, SIDES, SIGHT, STONE_BLOCKS,
  blockIds, inventoryCounts, isSheltered, isSolid, logIds, tableWithinReach
} = require('./observe')

const EXPLORE_DISTANCE = 32
const WOOD_TARGET = 4
const STONE_TARGET = 6
const FILLERS = ['dirt', 'cobblestone', 'stone', 'andesite', 'diorite', 'granite', 'sand', 'gravel']

const done = sentence => ({ ok: true, sentence })
const failed = sentence => ({ ok: false, sentence })

function remaining (ctx) {
  return Math.max(0, ctx.deadline - Date.now())
}

/**
 * Await `promise`, but no longer than `ms` or the time the routine has left.
 *
 * Giving up waiting does not stop the step itself. Until it settles it is
 * counted in `ctx.unfinished`, so the runner knows something is still going on
 * after the routine has returned and can take her out of the world.
 */
function within (ctx, ms, promise) {
  const limit = Math.min(ms, remaining(ctx))
  let timer
  const timeout = new Promise((resolve, reject) => {
    timer = setTimeout(() => {
      ctx.unfinished = (ctx.unfinished || 0) + 1
      const settled = () => { ctx.unfinished -= 1 }
      Promise.resolve(promise).then(settled, settled)
      reject(new Error('timed out'))
    }, limit)
  })
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer))
}

function stopMoving (bot) {
  try { bot.pathfinder.setGoal(null) } catch (e) {}
  try { bot.stopDigging() } catch (e) {}
}

async function walkTo (bot, ctx, goal, ms) {
  try {
    await within(ctx, ms, bot.pathfinder.goto(goal))
    return true
  } catch (e) {
    stopMoving(bot)
    return false
  }
}

function count (bot, predicate) {
  return bot.inventory.items().filter(i => predicate(i.name)).reduce((n, i) => n + i.count, 0)
}

function carried (bot, name) {
  return bot.inventory.items().find(i => i.name === name) || null
}

async function equipBest (bot, kind) {
  const name = bestTool(inventoryCounts(bot), kind)
  if (name) await bot.equip(carried(bot, name), 'hand')
  return name
}

// ---------------------------------------------------------------------------

async function lookAround (bot) {
  const yaw = bot.entity.yaw
  for (let quarter = 1; quarter <= 4; quarter++) {
    await bot.look(yaw + quarter * Math.PI / 2, 0)
    await bot.waitForTicks(8)
  }
  return done('Looked around.')
}

async function explore (bot, args, ctx) {
  const direction = String(args.direction || 'north')
  const vector = DIRECTIONS[direction]
  if (!vector) return failed(`Did not know which way "${direction}" is.`)
  const from = bot.entity.position.clone()
  const goal = new goals.GoalNearXZ(
    from.x + vector[0] * EXPLORE_DISTANCE, from.z + vector[1] * EXPLORE_DISTANCE, 3)
  await walkTo(bot, ctx, goal, 40000)
  const walked = Math.round(bot.entity.position.distanceTo(from))
  if (walked < 5) return failed(`Could not get anywhere going ${direction}.`)
  return done(`Walked ${walked} blocks ${direction}.`)
}

async function gatherWood (bot, args, ctx) {
  const isLog = name => name.endsWith('_log')
  const before = count(bot, isLog)
  const ids = logIds(bot)
  const skipped = new Set()
  while (count(bot, isLog) - before < WOOD_TARGET && remaining(ctx) > 3000) {
    const target = bot.findBlocks({ matching: ids, maxDistance: SIGHT, count: 12 })
      .find(position => !skipped.has(position.toString()))
    if (!target) break
    skipped.add(target.toString())
    try {
      await within(ctx, 30000, bot.collectBlock.collect(bot.blockAt(target)))
    } catch (e) {
      stopMoving(bot)
    }
  }
  const chopped = count(bot, isLog) - before
  if (chopped <= 0) return failed('Could not reach any wood.')
  return done('Chopped wood from the trees.')
}

async function ensureTable (bot, ctx) {
  const near = tableWithinReach(bot)
  if (near) return near
  if (!carried(bot, 'crafting_table')) return null
  await bot.equip(carried(bot, 'crafting_table'), 'hand')
  const feet = bot.entity.position.floored()
  const spots = [[1, 0], [-1, 0], [0, 1], [0, -1], [2, 0], [-2, 0], [0, 2], [0, -2], [1, 1], [-1, -1]]
  for (const [dx, dz] of spots) {
    const ground = bot.blockAt(feet.offset(dx, -1, dz))
    const space = bot.blockAt(feet.offset(dx, 0, dz))
    if (ground && space && ground.boundingBox === 'block' && space.name === 'air') {
      try {
        await within(ctx, 5000, bot.placeBlock(ground, new Vec3(0, 1, 0)))
        await bot.waitForTicks(5)
        return tableWithinReach(bot)
      } catch (e) {}
    }
  }
  return null
}

async function craftOnce (bot, itemName, times, table) {
  const item = bot.registry.itemsByName[itemName]
  const recipe = item && bot.recipesFor(item.id, null, 1, table || null)[0]
  if (!recipe) return false
  await bot.craft(recipe, times, table || null)
  // The inventory lags behind the craft; read it too early and it looks empty.
  await bot.waitForTicks(12)
  return true
}

async function craft (bot, args, ctx) {
  const wanted = String(args.item || '')
  if (!CRAFT_WHITELIST.includes(wanted)) return failed(`Did not know how to craft "${wanted}".`)
  const pretty = wanted.replace(/_/g, ' ')

  if (wanted === 'planks') {
    const log = bot.inventory.items().find(i => i.name.endsWith('_log'))
    if (!log) return failed('Had no logs to turn into planks.')
    const made = await craftOnce(bot, log.name.replace(/_log$/, '_planks'), Math.min(log.count, 4), null)
    return made ? done('Turned logs into planks.') : failed('Could not turn the logs into planks.')
  }

  const item = bot.registry.itemsByName[wanted]
  // Check the materials before putting a table down for nothing.
  if (bot.recipesFor(item.id, null, 1, true).length === 0) {
    return failed(`Did not have what it takes to craft ${pretty}.`)
  }
  const needsTable = bot.recipesFor(item.id, null, 1, null).length === 0
  let table = null
  if (needsTable) {
    table = await ensureTable(bot, ctx)
    if (!table) return failed(`Needed a crafting table to make the ${pretty}, and had none.`)
  }
  const made = await craftOnce(bot, wanted, 1, table)
  return made ? done(`Crafted ${pretty}.`) : failed(`Did not have what it takes to craft ${pretty}.`)
}

async function mineStone (bot, args, ctx) {
  if (!(await equipBest(bot, 'pickaxe'))) return failed('Had no pickaxe to mine with.')
  const isStone = name => name === 'cobblestone' || STONE_BLOCKS.includes(name)
  const before = count(bot, isStone)
  const ids = blockIds(bot, STONE_BLOCKS)
  const skipped = new Set()
  while (count(bot, isStone) - before < STONE_TARGET && remaining(ctx) > 3000) {
    const target = bot.findBlocks({ matching: ids, maxDistance: 24, count: 12 })
      .find(position => !skipped.has(position.toString()))
    if (!target) break
    skipped.add(target.toString())
    try {
      await within(ctx, 25000, bot.collectBlock.collect(bot.blockAt(target)))
    } catch (e) {
      stopMoving(bot)
    }
  }
  if (count(bot, isStone) - before <= 0) return failed('Could not get any stone.')
  return done('Mined stone.')
}

async function hunt (bot, args, ctx) {
  const here = bot.entity.position
  const target = bot.nearestEntity(e => ANIMALS.has(e.name) && e.position.distanceTo(here) <= SIGHT)
  if (!target) return failed('There was no animal close enough to hunt.')
  const name = target.name
  if (!(await equipBest(bot, 'sword'))) await equipBest(bot, 'axe')
  // An entity also stops being valid when it walks out of sight, so only its
  // death event counts as a kill.
  let killed = false
  const onDead = entity => { if (entity === target) killed = true }
  bot.on('entityDead', onDead)
  let lastSeen = target.position.clone()
  try {
    while (!killed && target.isValid && remaining(ctx) > 6000) {
      lastSeen = target.position.clone()
      if (bot.entity.position.distanceTo(target.position) > 3) {
        bot.pathfinder.setGoal(new goals.GoalFollow(target, 2), true)
      } else {
        await bot.lookAt(target.position.offset(0, (target.height || 1) * 0.6, 0), true)
        bot.attack(target)
      }
      await bot.waitForTicks(12)
    }
  } finally {
    bot.removeListener('entityDead', onDead)
    stopMoving(bot)
  }
  if (!killed) return failed(`The ${name} got away.`)
  // Walk onto the spot so the drops are picked up.
  await walkTo(bot, ctx, new goals.GoalNear(lastSeen.x, lastSeen.y, lastSeen.z, 1), 5000)
  await bot.waitForTicks(20)
  return done(`Hunted a ${name}.`)
}

async function eat (bot, args, ctx) {
  if (bot.food >= 20) return failed('Was not hungry enough to eat.')
  const name = FOODS.find(food => carried(bot, food))
  if (!name) return failed('Had nothing to eat.')
  await bot.equip(carried(bot, name), 'hand')
  try {
    await within(ctx, 8000, bot.consume())
  } catch (e) {
    return failed(`Could not eat the ${name.replace(/_/g, ' ')}.`)
  }
  return done(`Ate ${name.replace(/_/g, ' ')}.`)
}

async function drink (bot, args, ctx) {
  const water = bot.findBlock({ matching: blockIds(bot, ['water']), maxDistance: 16 })
  if (!water) return failed('There was no water close enough to drink.')
  const { x, y, z } = water.position
  if (!(await walkTo(bot, ctx, new goals.GoalNear(x, y, z, 2), 20000))) {
    return failed('Could not reach the water.')
  }
  await bot.lookAt(water.position.offset(0.5, 0.5, 0.5), true)
  await bot.waitForTicks(20)
  return done('Drank from the water.')
}

async function waitUntil (bot, ctx, ms, condition) {
  const end = Date.now() + Math.min(ms, remaining(ctx))
  while (Date.now() < end) {
    if (condition()) return true
    await bot.waitForTicks(2)
  }
  return condition()
}

/** Dig three blocks straight down and close the hole overhead. */
async function takeShelter (bot, args, ctx) {
  if (isSheltered(bot)) return done('Stayed sheltered in the burrow.')
  stopMoving(bot)
  const start = bot.entity.position.floored()
  await walkTo(bot, ctx, new goals.GoalBlock(start.x, start.y, start.z), 4000)
  for (let depth = 1; depth <= 4; depth++) {
    const below = bot.blockAt(start.offset(0, -depth, 0))
    if (!below || below.boundingBox !== 'block' || (depth < 4 && !below.diggable)) {
      return failed('The ground here was not safe to dig a burrow in.')
    }
  }
  for (let depth = 1; depth <= 3; depth++) {
    const below = bot.blockAt(start.offset(0, -depth, 0))
    try {
      if (bot.tool) await bot.tool.equipForBlock(below, {})
      await within(ctx, 10000, bot.dig(below))
    } catch (e) {
      return failed('Could not dig deep enough for a burrow.')
    }
    await waitUntil(bot, ctx, 3000, () => bot.entity.onGround && bot.entity.position.y <= start.y - depth + 0.2)
  }
  await bot.waitForTicks(15)
  const filler = bot.inventory.items().find(i => FILLERS.includes(i.name) || i.name.endsWith('_planks'))
  if (!filler) return failed('Dug down but had nothing to close the burrow with.')
  await bot.equip(filler, 'hand')
  const lid = start.offset(0, -1, 0)
  for (const [dx, dz] of SIDES) {
    const wall = lid.offset(dx, 0, dz)
    if (!isSolid(bot, wall)) continue
    try {
      await within(ctx, 4000, bot.placeBlock(bot.blockAt(wall), new Vec3(-dx, 0, -dz)))
      break
    } catch (e) {}
  }
  await bot.waitForTicks(5)
  if (!isSheltered(bot)) return failed('Dug a hole but could not close it overhead.')
  return done('Dug a burrow and closed it overhead.')
}

async function goHome (bot, args, ctx) {
  const { x, y, z } = args
  if (![x, y, z].every(Number.isFinite)) return failed('Did not know where home is.')
  const arrived = await walkTo(bot, ctx, new goals.GoalNear(x, y, z, 2), 40000)
  return arrived ? done('Walked back home.') : failed('Could not find a way home in time.')
}

async function rest (bot) {
  await bot.waitForTicks(100)
  return done('Rested for a while.')
}

const ACTIONS = {
  look_around: lookAround,
  explore,
  gather_wood: gatherWood,
  craft,
  mine_stone: mineStone,
  hunt,
  eat,
  drink,
  take_shelter: takeShelter,
  go_home: goHome,
  rest
}

module.exports = { ACTIONS, stopMoving, within }
