'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { createSession } = require('../session')

/** A login whose arrival the test decides, one attempt at a time. */
function fakeWorld () {
  const world = { attempts: [], left: [] }
  world.login = onGone => new Promise((resolve, reject) => {
    const bot = { entity: {}, id: world.attempts.length + 1 }
    world.attempts.push({ bot, arrive: () => resolve(bot), fail: e => reject(e), gone: () => onGone(bot) })
  })
  world.leave = async bot => { world.left.push(bot.id) }
  return world
}

const tick = () => new Promise(resolve => setImmediate(resolve))

test('starting a session logs her in once and returns her bot', async () => {
  const world = fakeWorld()
  const session = createSession(world)
  const first = session.start()
  const second = session.start()
  await tick()
  assert.equal(world.attempts.length, 1)
  world.attempts[0].arrive()
  assert.equal((await first).id, 1)
  assert.equal((await second).id, 1)
  assert.equal(session.connected(), true)
  assert.equal((await session.start()).id, 1)
  assert.equal(world.attempts.length, 1)
})

test('ending a session logs her out', async () => {
  const world = fakeWorld()
  const session = createSession(world)
  const started = session.start()
  await tick()
  world.attempts[0].arrive()
  await started
  await session.end()
  assert.deepEqual(world.left, [1])
  assert.equal(session.connected(), false)
  assert.equal(session.bot(), null)
})

test('a request to leave during a login sends the arriving bot away again', async () => {
  const world = fakeWorld()
  const session = createSession(world)
  const started = session.start()
  await tick()
  await session.end()
  world.attempts[0].arrive()
  await assert.rejects(started, e => e.code === 'session_ended' && e.status === 409)
  assert.deepEqual(world.left, [1])
  assert.equal(session.connected(), false)
})

test('someone who asks after the request to leave still gets her in the world', async () => {
  const world = fakeWorld()
  const session = createSession(world)
  const stale = session.start()
  await tick()
  await session.end()
  const wanted = session.start()
  world.attempts[0].arrive()
  await assert.rejects(stale, e => e.code === 'session_ended')
  await tick()
  assert.equal(world.attempts.length, 2)
  world.attempts[1].arrive()
  assert.equal((await wanted).id, 2)
  assert.deepEqual(world.left, [1])
  assert.equal(session.bot().id, 2)
})

test('a failed login is reported and the next start tries again', async () => {
  const world = fakeWorld()
  const session = createSession(world)
  const started = session.start()
  await tick()
  world.attempts[0].fail(new Error('no server'))
  await assert.rejects(started, /no server/)
  const again = session.start()
  await tick()
  world.attempts[1].arrive()
  assert.equal((await again).id, 2)
})

test('a bot that leaves by itself is forgotten, but not a newer one', async () => {
  const world = fakeWorld()
  const session = createSession(world)
  const started = session.start()
  await tick()
  world.attempts[0].arrive()
  await started
  world.attempts[0].gone()
  assert.equal(session.connected(), false)
  const again = session.start()
  await tick()
  world.attempts[1].arrive()
  await again
  world.attempts[0].gone()
  assert.equal(session.bot().id, 2)
})
