'use strict'
// What Jenbina has heard other players say: a short, bounded list, emptied
// each time it is read. A talk in progress takes its partner's lines for
// itself instead, so an answer is not also reported as something overheard.

function createHearing ({ self, limit = 20, maxLength = 256 }) {
  const kept = []
  const takers = new Map()

  /** Record one line from another player; her own lines and empty ones are ignored. */
  function hear (from, text, whisper) {
    if (typeof from !== 'string' || typeof text !== 'string') return
    if (from === self || text.trim() === '') return
    const line = { from, text: text.trim().slice(0, maxLength), whisper: !!whisper }
    const taker = takers.get(from)
    if (taker) return taker(line)
    kept.push(line)
    while (kept.length > limit) kept.shift()
  }

  /** Everything kept, oldest first; the list is empty afterwards. */
  function drain () {
    return kept.splice(0, kept.length)
  }

  /** Send `from`'s lines to `handler` until the returned function is called. */
  function take (from, handler) {
    takers.set(from, handler)
    return () => { if (takers.get(from) === handler) takers.delete(from) }
  }

  return { hear, drain, take }
}

module.exports = { createHearing }
