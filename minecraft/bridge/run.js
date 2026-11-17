'use strict'
// Runs one routine against a bot within a time budget and reports what really
// changed. Kept free of HTTP and of Mineflayer so it is unit-tested with a
// fake bot (`node --test`).

const { inventoryDiff, outcomeSummary } = require('./words')

const DIED = 'Died and woke up again at the spawn point. What was carried may be lost.'
const OVERRUN = Symbol('overrun')

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
  const ctx = { deadline: started + budgetMs, died: false }
  const onDeath = () => { ctx.died = true }
  // The listener stays until the result has been read: a death while pickups
  // settle is still a death in this action.
  bot.on('death', onDeath)
  try {
    const before = deps.inventoryCounts(bot)
    const work = Promise.resolve().then(() => routine(bot, args || {}, ctx))
    let timer
    const overrun = new Promise(resolve => { timer = setTimeout(() => resolve(OVERRUN), budgetMs + graceMs) })
    let result
    try {
      result = await Promise.race([work, overrun])
    } catch (e) {
      deps.stop(bot)
      result = { ok: false, sentence: `Tried to ${doing} but it did not work out (${e.message}).` }
    } finally {
      clearTimeout(timer)
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
        duration_ms: Date.now() - started,
        observation: null
      }
    }

    // Let pickups, crafts and a respawn settle before reading the result.
    await bot.waitForTicks(ctx.died ? 40 : 10)
    const { gained, lost } = inventoryDiff(before, deps.inventoryCounts(bot))
    return {
      ok: result.ok && !ctx.died,
      name,
      summary: ctx.died ? DIED : outcomeSummary(result.sentence, gained, lost),
      gained,
      lost,
      died: ctx.died,
      timed_out: false,
      duration_ms: Date.now() - started,
      observation: deps.observe(bot)
    }
  } finally {
    bot.removeListener('death', onDeath)
  }
}

module.exports = { DIED, runRoutine }
