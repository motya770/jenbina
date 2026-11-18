'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { EventEmitter } = require('node:events')
const { DIED, runRoutine } = require('../run')

function fakeBot (inventory = {}) {
  const bot = new EventEmitter()
  bot.inventory = { ...inventory }
  bot.ticksWaited = []
  bot.duringSettle = () => {}
  bot.waitForTicks = async ticks => {
    bot.ticksWaited.push(ticks)
    bot.duringSettle()
  }
  return bot
}

function deps (bot, log = []) {
  return {
    inventoryCounts: () => ({ ...bot.inventory }),
    observe: () => ({ food: 20 }),
    stop: () => log.push('stop'),
    disconnect: async () => { log.push('disconnect') }
  }
}

const options = (bot, routine, extra = {}) => ({
  bot, name: 'gather_wood', routine, args: {}, budgetMs: 1000, graceMs: 50, deps: deps(bot), ...extra
})

test('a finished routine reports what the inventory really gained', async () => {
  const bot = fakeBot({ stick: 1 })
  const outcome = await runRoutine(options(bot, async () => {
    bot.inventory.oak_log = 4
    return { ok: true, sentence: 'Chopped wood from the trees.' }
  }))
  assert.equal(outcome.ok, true)
  assert.equal(outcome.summary, 'Chopped wood from the trees. Gained 4 oak logs.')
  assert.deepEqual(outcome.gained, { oak_log: 4 })
  assert.equal(outcome.timed_out, false)
  assert.deepEqual(outcome.observation, { food: 20 })
  assert.equal(bot.listenerCount('death'), 0)
})

test('a routine that throws is a failed outcome, not an error', async () => {
  const bot = fakeBot()
  const log = []
  const outcome = await runRoutine(options(bot, async () => { throw new Error('no path') }, { deps: deps(bot, log) }))
  assert.equal(outcome.ok, false)
  assert.match(outcome.summary, /Tried to gather wood but it did not work out \(no path\)/)
  assert.deepEqual(log, ['stop'])
})

test('a routine that overruns is cut off by taking her out of the world', async () => {
  const bot = fakeBot()
  const log = []
  let finishLate
  const neverInTime = () => new Promise(resolve => { finishLate = resolve })
  const outcome = await runRoutine(options(bot, neverInTime, { budgetMs: 20, graceMs: 20, deps: deps(bot, log) }))
  assert.equal(outcome.ok, false)
  assert.equal(outcome.timed_out, true)
  assert.equal(outcome.observation, null)
  assert.match(outcome.summary, /Ran out of time trying to gather wood/)
  assert.deepEqual(log, ['stop', 'disconnect'])
  // The late routine finishing afterwards must not blow anything up.
  finishLate({ ok: true, sentence: 'Too late.' })
  assert.equal(bot.listenerCount('death'), 0)
})

test('dying during the routine fails the action', async () => {
  const bot = fakeBot({ oak_log: 3 })
  const outcome = await runRoutine(options(bot, async () => {
    bot.emit('death')
    bot.inventory = {}
    return { ok: true, sentence: 'Chopped wood from the trees.' }
  }))
  assert.equal(outcome.ok, false)
  assert.equal(outcome.died, true)
  assert.equal(outcome.summary, DIED)
  assert.deepEqual(bot.ticksWaited, [40])
})

test('dying while the result settles still counts as dying in this action', async () => {
  const bot = fakeBot()
  bot.duringSettle = () => bot.emit('death')
  const outcome = await runRoutine(options(bot, async () => ({ ok: true, sentence: 'Rested for a while.' })))
  assert.equal(outcome.died, true)
  assert.equal(outcome.ok, false)
  assert.equal(outcome.summary, DIED)
})

test('the routine is told when its budget ends', async () => {
  const bot = fakeBot()
  let deadline
  const before = Date.now()
  await runRoutine(options(bot, async (b, args, ctx) => {
    deadline = ctx.deadline
    return { ok: true, sentence: 'Done.' }
  }, { budgetMs: 5000 }))
  assert.ok(deadline >= before + 5000 && deadline <= Date.now() + 5000)
})

test('a bot that leaves the world mid-routine is an error, not a wait for ticks', async () => {
  const bot = fakeBot()
  const hangs = () => new Promise(() => {})
  const running = runRoutine(options(bot, hangs, { budgetMs: 60000, graceMs: 60000 }))
  setImmediate(() => bot.emit('end', 'socketClosed'))
  await assert.rejects(running, /the connection to the world closed/)
  assert.equal(bot.listenerCount('death'), 0)
  assert.equal(bot.listenerCount('end'), 0)
})

test('a bot that leaves while the result settles does not hang the action', async () => {
  const bot = fakeBot()
  // Like Mineflayer after a disconnect: the ticks never come.
  bot.waitForTicks = () => new Promise(() => {})
  const running = runRoutine(options(bot, async () => {
    setImmediate(() => bot.emit('end', 'socketClosed'))
    return { ok: true, sentence: 'Rested for a while.' }
  }))
  await assert.rejects(running, /the connection to the world closed/)
  assert.equal(bot.listenerCount('end'), 0)
})

test('a step still going after the routine returned takes her out of the world', async () => {
  const bot = fakeBot({ bread: 1 })
  const log = []
  const outcome = await runRoutine(options(bot, async (b, args, ctx) => {
    ctx.unfinished += 1          // what `within` records when it stops waiting
    return { ok: false, sentence: 'Could not eat the bread.' }
  }, { deps: { ...deps(bot, log), observe: () => { log.push('observe'); return { food: 12 } } } }))
  assert.equal(outcome.ok, false)
  assert.equal(outcome.left_world, true)
  assert.deepEqual(outcome.observation, { food: 12 })
  // Stopped first, read while she is still there, and only then disconnected.
  assert.deepEqual(log, ['stop', 'observe', 'disconnect'])
})

test('a step that stops when told to does not cost her the session', async () => {
  const bot = fakeBot()
  const log = []
  let ctxSeen
  const d = deps(bot, log)
  d.stop = () => { log.push('stop'); ctxSeen.unfinished -= 1 }   // the walk rejects once stopped
  const outcome = await runRoutine(options(bot, async (b, args, ctx) => {
    ctxSeen = ctx
    ctx.unfinished += 1
    return { ok: false, sentence: 'Could not reach the water.' }
  }, { deps: d }))
  assert.equal(outcome.left_world, false)
  assert.deepEqual(log, ['stop'])
})
