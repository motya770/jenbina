'use strict'
// Pure helpers: no Mineflayer here, so these are unit-tested with `node --test`.

const TIERS = ['wooden', 'stone', 'iron', 'golden', 'diamond', 'netherite']
const TOOL_KINDS = ['pickaxe', 'axe', 'sword']

// Names that read wrong with a plural "s".
const MASS_NOUNS = new Set([
  'beef', 'mutton', 'leather', 'wool', 'cobblestone', 'dirt', 'sand', 'gravel',
  'flint', 'coal', 'wheat', 'rotten_flesh', 'string', 'stone', 'chicken',
  'cooked_beef', 'cooked_mutton', 'cooked_chicken', 'bread'
])

const DIRECTIONS = {
  north: [0, -1],
  south: [0, 1],
  east: [1, 0],
  west: [-1, 0]
}

/** What an inventory gained and lost between two `{name: count}` snapshots. */
function inventoryDiff (before, after) {
  const gained = {}
  const lost = {}
  for (const name of new Set([...Object.keys(before), ...Object.keys(after)])) {
    const delta = (after[name] || 0) - (before[name] || 0)
    if (delta > 0) gained[name] = delta
    if (delta < 0) lost[name] = -delta
  }
  return { gained, lost }
}

/** "oak_log" x4 -> "4 oak logs"; "beef" x2 -> "2 beef". */
function itemPhrase (name, count) {
  const words = name.replace(/_/g, ' ')
  if (count === 1 || MASS_NOUNS.has(name) || words.endsWith('s')) return `${count} ${words}`
  return `${count} ${words}s`
}

/** {oak_log: 4, stick: 1} -> "4 oak logs and 1 stick". Empty -> "". */
function itemsPhrase (counts) {
  const parts = Object.keys(counts).sort().map(name => itemPhrase(name, counts[name]))
  if (parts.length <= 1) return parts.join('')
  return parts.slice(0, -1).join(', ') + ' and ' + parts[parts.length - 1]
}

/** The routine's own sentence, then what the inventory really gained and used. */
function outcomeSummary (sentence, gained, lost) {
  let text = sentence.trim()
  const got = itemsPhrase(gained)
  const used = itemsPhrase(lost)
  if (got) text += ` Gained ${got}.`
  if (used) text += ` Used ${used}.`
  return text
}

/** True when the inventory already holds this tool kind at the same tier or better. */
function hasSameOrBetterTool (inventory, toolName) {
  const [tier, kind] = splitTool(toolName)
  if (kind === null) return false
  const wanted = TIERS.indexOf(tier)
  return Object.keys(inventory).some(name => {
    const [otherTier, otherKind] = splitTool(name)
    return otherKind === kind && TIERS.indexOf(otherTier) >= wanted && inventory[name] > 0
  })
}

function splitTool (name) {
  for (const kind of TOOL_KINDS) {
    if (name.endsWith('_' + kind)) {
      const tier = name.slice(0, -kind.length - 1)
      if (TIERS.includes(tier)) return [tier, kind]
    }
  }
  return [null, null]
}

/** The best tool of a kind in the inventory, as an item name, or null. */
function bestTool (inventory, kind) {
  for (const tier of [...TIERS].reverse()) {
    const name = `${tier}_${kind}`
    if ((inventory[name] || 0) > 0) return name
  }
  return null
}

module.exports = {
  DIRECTIONS,
  TIERS,
  bestTool,
  hasSameOrBetterTool,
  inventoryDiff,
  itemPhrase,
  itemsPhrase,
  outcomeSummary
}
