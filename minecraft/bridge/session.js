'use strict'
// Who is in the world right now: one bot at most. Kept free of HTTP and of
// Mineflayer so it is unit-tested with a fake login (`node --test`).
//
// Logging in takes seconds. Everyone who asks while it is under way shares the
// one attempt, and a request to leave during it wins: the bot that arrives
// afterwards is sent away again instead of being left standing in the world.

function sessionEnded () {
  const error = new Error('She was asked to leave the world while she was still joining it.')
  error.status = 409
  error.code = 'session_ended'
  return error
}

/**
 * @param {object} options
 * @param {Function} options.login   async (onGone) => bot; calls onGone(bot) when the bot leaves by itself
 * @param {Function} options.leave   async (bot) => void; logs that bot out
 */
function createSession ({ login, leave }) {
  let bot = null
  let connecting = null
  // Counts requests to leave; a login that started under an older number is stale.
  let epoch = 0

  const connected = () => bot !== null && bot.entity != null

  function join () {
    const mine = epoch
    return login(gone => { if (bot === gone) bot = null }).then(async arrived => {
      if (mine !== epoch) {
        await leave(arrived)
        throw sessionEnded()
      }
      bot = arrived
      return arrived
    }).finally(() => { connecting = null })
  }

  /** Log her in if she is not in the world, and return her bot. */
  async function start () {
    const asked = epoch
    for (;;) {
      if (connected()) return bot
      if (connecting === null) connecting = join()
      try {
        return await connecting
      } catch (e) {
        // Someone who asked after the request to leave shared a stale
        // attempt; they still want her in the world, so try again.
        if (!(e && e.code === 'session_ended') || asked !== epoch) throw e
      }
    }
  }

  /** Log her out, including out of a login that has not finished yet. */
  async function end () {
    epoch += 1
    if (bot === null) return
    const leaving = bot
    bot = null
    await leave(leaving)
  }

  return { bot: () => bot, connected, start, end }
}

module.exports = { createSession }
