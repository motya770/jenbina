'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const {
  DIRECTIONS, bestTool, hasSameOrBetterTool, inventoryDiff, itemPhrase, itemsPhrase, outcomeSummary
} = require('../words')

test('inventoryDiff reports what was gained and what was used', () => {
  const diff = inventoryDiff({ oak_log: 4, stick: 2 }, { oak_planks: 16, stick: 1 })
  assert.deepEqual(diff.gained, { oak_planks: 16 })
  assert.deepEqual(diff.lost, { oak_log: 4, stick: 1 })
})

test('inventoryDiff of an unchanged inventory is empty', () => {
  assert.deepEqual(inventoryDiff({ dirt: 3 }, { dirt: 3 }), { gained: {}, lost: {} })
})

test('itemPhrase pluralises countable things only', () => {
  assert.equal(itemPhrase('oak_log', 4), '4 oak logs')
  assert.equal(itemPhrase('oak_log', 1), '1 oak log')
  assert.equal(itemPhrase('beef', 2), '2 beef')
  assert.equal(itemPhrase('oak_planks', 8), '8 oak planks')
})

test('itemsPhrase joins in a stable order', () => {
  assert.equal(itemsPhrase({}), '')
  assert.equal(itemsPhrase({ stick: 4 }), '4 sticks')
  assert.equal(itemsPhrase({ stick: 1, oak_log: 2 }), '2 oak logs and 1 stick')
  assert.equal(itemsPhrase({ stick: 1, oak_log: 2, beef: 1 }), '1 beef, 2 oak logs and 1 stick')
})

test('outcomeSummary appends real gains and uses to the sentence', () => {
  assert.equal(outcomeSummary('Looked around.', {}, {}), 'Looked around.')
  assert.equal(
    outcomeSummary('Crafted wooden pickaxe.', { wooden_pickaxe: 1 }, { oak_planks: 3, stick: 2 }),
    'Crafted wooden pickaxe. Gained 1 wooden pickaxe. Used 3 oak planks and 2 sticks.')
})

test('hasSameOrBetterTool compares tiers within one kind of tool', () => {
  assert.equal(hasSameOrBetterTool({ wooden_pickaxe: 1 }, 'wooden_pickaxe'), true)
  assert.equal(hasSameOrBetterTool({ stone_pickaxe: 1 }, 'wooden_pickaxe'), true)
  assert.equal(hasSameOrBetterTool({ wooden_pickaxe: 1 }, 'stone_pickaxe'), false)
  assert.equal(hasSameOrBetterTool({ stone_axe: 1 }, 'wooden_pickaxe'), false)
  assert.equal(hasSameOrBetterTool({ stick: 4 }, 'stick'), false)
})

test('bestTool picks the highest tier carried', () => {
  assert.equal(bestTool({ wooden_pickaxe: 1, stone_pickaxe: 1 }, 'pickaxe'), 'stone_pickaxe')
  assert.equal(bestTool({ wooden_sword: 1 }, 'pickaxe'), null)
})

test('north is toward negative z, as in Minecraft', () => {
  assert.deepEqual(DIRECTIONS.north, [0, -1])
  assert.deepEqual(DIRECTIONS.east, [1, 0])
})
