'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const { createHearing } = require('../hearing')

test('keeps what others say and leaves her own lines out', () => {
  const hearing = createHearing({ self: 'Jenbina' })
  hearing.hear('Mira', ' hello ', false)
  hearing.hear('Jenbina', 'hi', false)
  assert.deepEqual(hearing.drain(), [{ from: 'Mira', text: 'hello', whisper: false }])
  assert.deepEqual(hearing.drain(), [])
})

test('keeps only the last 20 and cuts a line to 256 characters', () => {
  const hearing = createHearing({ self: 'Jenbina' })
  for (let i = 0; i < 25; i++) hearing.hear('Mira', `line ${i}`, false)
  hearing.hear('Tobin', 'x'.repeat(400), true)
  const lines = hearing.drain()
  assert.equal(lines.length, 20)
  assert.equal(lines[0].text, 'line 6')
  assert.equal(lines[19].text.length, 256)
  assert.equal(lines[19].whisper, true)
})

test('a taker gets its partner\'s lines and nobody else\'s', () => {
  const hearing = createHearing({ self: 'Jenbina' })
  const got = []
  const release = hearing.take('Mira', line => got.push(line.text))
  hearing.hear('Mira', 'to the talk', false)
  hearing.hear('Tobin', 'to the list', false)
  release()
  hearing.hear('Mira', 'late piece', false)
  assert.deepEqual(got, ['to the talk'])
  assert.deepEqual(hearing.drain().map(l => l.text), ['to the list', 'late piece'])
})

test('ignores empty and non-text input', () => {
  const hearing = createHearing({ self: 'Jenbina' })
  hearing.hear('Mira', '', false); hearing.hear('Mira', undefined, false); hearing.hear(null, 'x', false)
  hearing.hear('Mira', '   ', false)
  assert.deepEqual(hearing.drain(), [])
})

test('releasing an old taker does not silence a newer one', () => {
  const hearing = createHearing({ self: 'Jenbina' })
  const first = []
  const second = []
  const releaseFirst = hearing.take('Mira', line => first.push(line.text))
  const releaseSecond = hearing.take('Mira', line => second.push(line.text))
  releaseFirst()
  hearing.hear('Mira', 'still talking', false)
  releaseSecond()
  assert.deepEqual([first, second], [[], ['still talking']])
})
