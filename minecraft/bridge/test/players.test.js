'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { Vec3 } = require('vec3')
const { playersAround } = require('../observe')

const at = (x, z) => ({ position: new Vec3(x, 64, z) })
function fakeBot (players) {
  return { username: 'Jenbina', entity: at(0, 0), players }
}

test('near players come nearest first with whole distances, herself left out', () => {
  const bot = fakeBot({ Jenbina: { entity: at(0, 0) }, Tobin: { entity: at(20, 0) }, Mira: { entity: at(6, 0) } })
  assert.deepEqual(playersAround(bot, 32), {
    near: [{ name: 'Mira', distance: 6 }, { name: 'Tobin', distance: 20 }], elsewhere: []
  })
})

test('a player out of sight or without an entity is elsewhere', () => {
  const bot = fakeBot({ Mira: { entity: at(40, 0) }, Tobin: {} })
  assert.deepEqual(playersAround(bot, 32), { near: [], elsewhere: ['Mira', 'Tobin'] })
})

test('a name that is not a plain name is not reported', () => {
  const bot = fakeBot({ 'Bad Name': { entity: at(1, 0) }, 'x"y': {}, ['A'.repeat(17)]: {}, ab: {}, Mira: {} })
  assert.deepEqual(playersAround(bot, 32), { near: [], elsewhere: ['Mira'] })
})

test('at most five of each', () => {
  const players = {}
  for (let i = 0; i < 8; i++) { players[`Near${i}`] = { entity: at(i + 1, 0) }; players[`Far${i}`] = {} }
  const around = playersAround(fakeBot(players), 32)
  assert.equal(around.near.length, 5); assert.equal(around.elsewhere.length, 5)
  assert.deepEqual(around.near.map(p => p.name), ['Near0', 'Near1', 'Near2', 'Near3', 'Near4'])
})

test('no player list at all means nobody', () => {
  assert.deepEqual(playersAround({ username: 'Jenbina', entity: at(0, 0) }, 32), { near: [], elsewhere: [] })
})
