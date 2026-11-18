'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { Vec3 } = require('vec3')
const { ACTIONS } = require('../actions')
const { createHearing } = require('../hearing')
const { cleanLine, sayAndListen } = require('../say')

const setup = (online = true) => {
  const hearing = createHearing({ self: 'Jenbina' })
  const sent = []
  return { hearing, sent, isOnline: () => online, whisper: (to, text) => sent.push([to, text]) }
}

test('an answer in time is returned with the pieces that follow it', async () => {
  const s = setup()
  const talk = sayAndListen({ ...s, to: 'Mira', text: 'Hello', waitMs: 500, lingerMs: 60 })
  s.hearing.hear('Mira', 'Hi there.', false)
  s.hearing.hear('Mira', 'Nice day.', false)
  const result = await talk
  assert.equal(result.answered, true)
  assert.deepEqual(result.heard.map(l => l.text), ['Hi there.', 'Nice day.'])
  assert.deepEqual(s.sent, [['Mira', 'Hello']])
})

test('no answer ends at the wait, and a later piece goes to the list', async () => {
  const s = setup()
  const result = await sayAndListen({ ...s, to: 'Mira', text: 'Hello', waitMs: 40, lingerMs: 20 })
  assert.deepEqual({ ok: result.ok, answered: result.answered, heard: result.heard }, { ok: true, answered: false, heard: [] })
  s.hearing.hear('Mira', 'sorry, what?', false)
  assert.deepEqual(s.hearing.drain().map(l => l.text), ['sorry, what?'])
})

test('someone else speaking is not the answer', async () => {
  const s = setup()
  const talk = sayAndListen({ ...s, to: 'Mira', text: 'Hello', waitMs: 40, lingerMs: 20 })
  s.hearing.hear('Tobin', 'morning', false)
  assert.equal((await talk).answered, false)
  assert.deepEqual(s.hearing.drain().map(l => l.from), ['Tobin'])
})

test('nothing is whispered to someone who is not in the world', async () => {
  const s = setup(false)
  const result = await sayAndListen({ ...s, to: 'Mira', text: 'Hello', waitMs: 40 })
  assert.equal(result.reason, 'not_online'); assert.deepEqual(s.sent, [])
})

test('a whisper that cannot be sent is reported and the partner is released', async () => {
  const s = setup()
  s.whisper = () => { throw new Error('socket closed') }
  const result = await sayAndListen({ ...s, to: 'Mira', text: 'Hello', waitMs: 40 })
  assert.deepEqual(result, { ok: false, answered: false, heard: [], reason: 'not_sent' })
  s.hearing.hear('Mira', 'anyone?', false)
  assert.deepEqual(s.hearing.drain().map(l => l.text), ['anyone?'])
})

test('her line is one line and never a command', () => {
  assert.equal(cleanLine('  /op Jenbina\nplease '), 'op Jenbina please')
  assert.equal(cleanLine('//x'), 'x')
  assert.equal(cleanLine(undefined), '')
  assert.equal(cleanLine(' / '), '')
})

test('her line is short enough to be one whisper', () => {
  assert.equal(cleanLine('y'.repeat(300)).length, 200)
})

test('her line cannot run a command of the one she talks to', () => {
  // Mindcraft runs any !word in a player's message as a command.
  assert.equal(cleanLine('Hi!goal("dig forever")'), 'Hi! goal("dig forever")')
  assert.equal(cleanLine('!stop'), '! stop')
  assert.equal(cleanLine('Wow! Nice!!'), 'Wow! Nice!!')
})

const walker = (players, goto) => ({
  entity: { position: new Vec3(0, 64, 0) },
  players,
  pathfinder: { setGoal () {}, goto },
  stopDigging () {}
})
const ctx = () => ({ deadline: Date.now() + 30000 })

test('she walks up to a player she can see', async () => {
  const goals = []
  const bot = walker({ Mira: { entity: { position: new Vec3(10, 64, 0) } } }, async goal => { goals.push(goal) })
  const result = await ACTIONS.approach_player(bot, { name: 'Mira' }, ctx())
  assert.deepEqual(result, { ok: true, sentence: 'Walked up to Mira.' })
  assert.deepEqual([goals[0].x, goals[0].y, goals[0].z, goals[0].rangeSq], [10, 64, 0, 9])
})

test('she does not walk when she is already beside them', async () => {
  let walked = false
  const bot = walker({ Mira: { entity: { position: new Vec3(2, 64, 0) } } }, async () => { walked = true })
  assert.equal((await ACTIONS.approach_player(bot, { name: 'Mira' }, ctx())).ok, true)
  assert.equal(walked, false)
})

test('she says so when she cannot see or reach them', async () => {
  const unseen = walker({ Mira: {} }, async () => {})
  assert.deepEqual(await ACTIONS.approach_player(unseen, { name: 'Mira' }, ctx()), { ok: false, sentence: 'Could not see Mira.' })
  const blocked = walker({ Mira: { entity: { position: new Vec3(10, 64, 0) } } }, async () => { throw new Error('no path') })
  assert.deepEqual(await ACTIONS.approach_player(blocked, { name: 'Mira' }, ctx()), { ok: false, sentence: 'Could not get to Mira.' })
})

test('a name that is not a plain name is never walked to or repeated', async () => {
  const bot = walker({ 'Bad Name': { entity: { position: new Vec3(10, 64, 0) } } }, async () => {})
  assert.deepEqual(await ACTIONS.approach_player(bot, { name: 'Bad Name' }, ctx()), { ok: false, sentence: 'Could not see them.' })
})
