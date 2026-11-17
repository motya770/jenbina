'use strict'
// Runs one routine against a bot within a time budget and reports what really
// changed. Kept free of HTTP and of Mineflayer so it is unit-tested with a
// fake bot (`node --test`).

const { inventoryDiff, outcomeSummary } = require('./words')

const DIED = 'Died and woke up again at the spawn point. What was carried may be lost.'
const CUT_OFF = 'the connection to the world closed'
const OVERRUN = Symbol('overrun')
const GONE = Symbol('gone')
const TICK_MS = 50

/**
 * Wait `ticks` game ticks, but never forever: a bot that has left the world
 * gets no more ticks, and its `waitForTicks` would never return.
 */
function settle (bot, ticks) {
  return new Promise(resolve => {
    let timer
    const finish = () => {
      clearTimeout(timer)
      bot.removeListener('end', finish)
      resolve()
    }
    timer = setTimeout(finish, ticks * TICK_MS * 4 + 1000)
    bot.once('end', finish)
    Promise.resolve().then(() => bot.waitForTicks(ticks)).then(finish, finish)
  })
}

/**
 * @param {object} options
 * @param {object} options.bot            the Mineflayer bot (an EventEmitter with waitForTicks)
 * @param {string} options.name           the action's name, for sentences
 * @param {Function} options.routine      async (bot, args, ctx) => { ok, sentence }
 * @param {object} [options.args]
 * @param {number} options.budgetMs       what the routine was promised
 * @param {number} options.graceMs        how long past the budget it may take to return by itself
 * @param {object} options.deps           { inventoryCounts(bot), observe(bot), stop(bot), disconnect(bot) }
 */
async function runRoutine ({ bot, name, routine, args, budgetMs, graceMs, deps }) {
  const started = Date.now()
  const doing = name.replace(/_/g, ' ')
  // `unfinished` counts steps the routine gave up waiting for that are still
  // going on (see `within` in actions.js).
  const ctx = { deadline: started + budgetMs, died: false, unfinished: 0 }
  const onDeath = () => { ctx.died = true }
  let gone = false
  let tellGone
  const left = new Promise(resolve => { tellGone = resolve })
  const onEnd = () => { gone = true; tellGone(GONE) }
  // The listener stays until the result has been read: a death while pickups
  // settle is still a death in this action.
  bot.on('death', onDeath)
  bot.once('end', onEnd)
  try {
    const before = deps.inventoryCounts(bot)
    const work = Promise.resolve().then(() => routine(bot, args || {}, ctx))
    let timer
    const overrun = new Promise(resolve => { timer = setTimeout(() => resolve(OVERRUN), budgetMs + graceMs) })
    let result
    try {
      result = await Promise.race([work, overrun, left])
    } catch (e) {
      deps.stop(bot)
      result = { ok: false, sentence: `Tried to ${doing} but it did not work out (${e.message}).` }
    } finally {
      clearTimeout(timer)
    }

    if (result === GONE || gone) {
      // Kicked, or the server stopped: there is nothing left to read, and the
      // caller must hear that rather than wait for ticks that will not come.
      work.catch(() => {})
      throw new Error(CUT_OFF)
    }

    if (result === OVERRUN) {
      // The routine is still running and cannot be cancelled. She leaves the
      // world, so it cannot go on changing things after this report.
      work.catch(() => {})
      deps.stop(bot)
      await deps.disconnect(bot)
      return {
        ok: false,
        name,
        summary: `Ran out of time trying to ${doing}, and left the world.`,
        gained: {},
        lost: {},
        died: ctx.died,
        timed_out: true,
        left_world: true,
        duration_ms: Date.now() - started,
        observation: null
      }
    }

    // A step the routine stopped waiting for may still be going on (eating,
    // digging). Stop what can be stopped before the result is read.
    if (ctx.unfinished > 0) deps.stop(bot)
    // Let pickups, crafts and a respawn settle before reading the result.
    await settle(bot, ctx.died ? 40 : 10)
    if (gone) throw new Error(CUT_OFF)
    const { gained, lost } = inventoryDiff(before, deps.inventoryCounts(bot))
    const outcome = {
      ok: result.ok && !ctx.died,
      name,
      summary: ctx.died ? DIED : outcomeSummary(result.sentence, gained, lost),
      gained,
      lost,
      died: ctx.died,
      timed_out: false,
      left_world: false,
      duration_ms: Date.now() - started,
      observation: deps.observe(bot)
    }
    if (ctx.unfinished > 0) {
      // It is still going and cannot be cancelled. She leaves the world, so
      // it cannot finish after this report says what happened.
      await deps.disconnect(bot)
      outcome.left_world = true
    }
    return outcome
  } finally {
    bot.removeListener('death', onDeath)
    bot.removeListener('end', onEnd)
  }
}

module.exports = { CUT_OFF, DIED, runRoutine, settle }
