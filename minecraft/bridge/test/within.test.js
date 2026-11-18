'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { within } = require('../actions')

const ctxFor = ms => ({ deadline: Date.now() + ms, unfinished: 0 })

test('a step that finishes in time is not counted as unfinished', async () => {
  const ctx = ctxFor(1000)
  assert.equal(await within(ctx, 500, Promise.resolve('done')), 'done')
  assert.equal(ctx.unfinished, 0)
})

test('a step that is still going after its limit is counted until it settles', async () => {
  const ctx = ctxFor(1000)
  let finish
  const eating = new Promise(resolve => { finish = resolve })
  await assert.rejects(within(ctx, 10, eating), /timed out/)
  assert.equal(ctx.unfinished, 1)
  finish()
  await new Promise(resolve => setImmediate(resolve))
  assert.equal(ctx.unfinished, 0)
})

test('a step that fails late is no longer counted either', async () => {
  const ctx = ctxFor(1000)
  let abort
  const digging = new Promise((resolve, reject) => { abort = reject })
  await assert.rejects(within(ctx, 10, digging), /timed out/)
  abort(new Error('Digging aborted'))
  await new Promise(resolve => setImmediate(resolve))
  assert.equal(ctx.unfinished, 0)
})
