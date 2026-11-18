'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { EventEmitter } = require('node:events')
const { Vec3 } = require('vec3')
const { ACTIONS } = require('../actions')

/** A bot standing next to `target`; `eachTick` runs on every wait. */
function fakeBot (target, eachTick) {
  const bot = new EventEmitter()
  bot.entity = { position: new Vec3(0, 64, 0) }
  bot.inventory = { items: () => [] }
  bot.pathfinder = { setGoal () {}, goto: async () => {} }
  bot.stopDigging = () => {}
  bot.nearestEntity = match => (match(target) ? target : null)
  bot.lookAt = async () => {}
  bot.attacks = 0
  bot.attack = () => { bot.attacks += 1 }
  bot.ticks = 0
  bot.waitForTicks = async () => {
    bot.ticks += 1
    eachTick(bot)
    await new Promise(resolve => setImmediate(resolve))
  }
  return bot
}

const cow = () => ({ name: 'cow', isValid: true, height: 1.4, position: new Vec3(1, 64, 0) })
const ctx = () => ({ deadline: Date.now() + 30000 })

test('an animal that walks out of sight was not hunted', async () => {
  const target = cow()
  const bot = fakeBot(target, b => { if (b.ticks === 2) target.isValid = false })
  const result = await ACTIONS.hunt(bot, {}, ctx())
  assert.equal(result.ok, false)
  assert.equal(result.sentence, 'The cow got away.')
  assert.equal(bot.listenerCount('entityDead'), 0)
})

test('an animal whose death was seen was hunted', async () => {
  const target = cow()
  const bot = fakeBot(target, b => {
    if (b.ticks === 2) {
      b.emit('entityDead', target)
      target.isValid = false
    }
  })
  const result = await ACTIONS.hunt(bot, {}, ctx())
  assert.equal(result.ok, true)
  assert.equal(result.sentence, 'Hunted a cow.')
  assert.ok(bot.attacks >= 1)
})

test('another animal dying nearby does not count', async () => {
  const target = cow()
  const bot = fakeBot(target, b => {
    if (b.ticks === 1) b.emit('entityDead', { name: 'pig' })
    if (b.ticks === 2) target.isValid = false
  })
  assert.equal((await ACTIONS.hunt(bot, {}, ctx())).ok, false)
})

test('with no animal in sight there is nothing to hunt', async () => {
  const bot = fakeBot({ name: 'zombie', position: new Vec3(1, 64, 0) }, () => {})
  const result = await ACTIONS.hunt(bot, {}, ctx())
  assert.equal(result.ok, false)
  assert.match(result.sentence, /no animal close enough/)
})
