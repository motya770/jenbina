'use strict'
// Saying one line to another player and waiting for the answer. Kept free of
// HTTP and of Mineflayer so it is unit-tested with a fake whisper
// (`node --test`).

// Short enough that Mineflayer sends it as one whisper, never split in two.
const MAX_LINE = 200

/**
 * Make `text` safe to send as her line: one line, never a server command
 * (no leading "/"), and never a command of the one she talks to (Mindcraft
 * runs any "!word" in a player's message, so "!" never touches a word).
 */
function cleanLine (text) {
  if (typeof text !== 'string') return ''
  return text
    .replace(/\s+/g, ' ')
    .replace(/^[\s/]+/, '')
    .replace(/!(?=\w)/g, '! ')
    .slice(0, MAX_LINE)
    .trim()
}

/**
 * Whisper `text` to `to` and collect what they say back.
 *
 * Waits up to `waitMs` for their first line, then `lingerMs` more for the
 * pieces that follow it. A line that comes later than that is not lost: the
 * hearing keeps it as something overheard.
 *
 * @returns {Promise<{ok: boolean, answered: boolean, heard: object[], reason?: string}>}
 */
function sayAndListen ({ hearing, whisper, isOnline, to, text, waitMs, lingerMs = 2000 }) {
  if (!isOnline(to)) return Promise.resolve({ ok: false, answered: false, heard: [], reason: 'not_online' })
  return new Promise(resolve => {
    const heard = []
    let timer
    let release = () => {}
    const finish = result => {
      clearTimeout(timer)
      release()
      resolve(result)
    }
    const listened = () => finish({ ok: true, answered: heard.length > 0, heard })
    release = hearing.take(to, line => {
      heard.push(line)
      if (heard.length > 1) return
      clearTimeout(timer)
      timer = setTimeout(listened, lingerMs)
    })
    timer = setTimeout(listened, waitMs)
    try {
      whisper(to, cleanLine(text))
    } catch (e) {
      finish({ ok: false, answered: false, heard: [], reason: 'not_sent' })
    }
  })
}

module.exports = { MAX_LINE, cleanLine, sayAndListen }
