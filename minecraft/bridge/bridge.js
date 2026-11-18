'use strict'
// Jenbina's body in Minecraft. A small HTTP server on localhost that logs in
// as her with Mineflayer and offers three verbs to her Python mind: observe,
// act and say. It keeps what other players say, hands it over with each
// observation, and says only the one line it is given, as a whisper.
//
//   GET  /health          -> { ok, connected, version }
//   POST /session/start   -> log in if needed, then { ok, observation }
//   POST /session/end     -> log out
//   GET  /observe         -> the current observation
//   POST /act             -> { name, args?, budget_ms? } -> the outcome
//   POST /say             -> { to, text, wait_ms? } -> { ok, answered, heard }
//
// Every observation carries `heard`: what was said since the last one.

const http = require('node:http')
const mineflayer = require('mineflayer')
const { pathfinder, Movements } = require('mineflayer-pathfinder')
const collectBlock = require('mineflayer-collectblock').plugin
const { ACTIONS, stopMoving } = require('./actions')
const { createHearing } = require('./hearing')
const { PLAIN_NAME, inventoryCounts, observe } = require('./observe')
const { runRoutine } = require('./run')
const { cleanLine, sayAndListen } = require('./say')
const { createSession } = require('./session')

const MC_HOST = process.env.MC_HOST || '127.0.0.1'
const MC_PORT = Number(process.env.MC_PORT || 25565)
const MC_USERNAME = process.env.MC_USERNAME || 'Jenbina'
const MC_VERSION = process.env.MC_VERSION || '1.21.4'
const BRIDGE_PORT = Number(process.env.BRIDGE_PORT || 3010)
const VIEWER_PORT = process.env.VIEWER_PORT ? Number(process.env.VIEWER_PORT) : null

const LOGIN_TIMEOUT_MS = 20000
const DEFAULT_BUDGET_MS = 45000
const MAX_BUDGET_MS = 120000
// Past its budget a routine has this long to notice and return by itself.
const OVERRUN_GRACE_MS = 8000
const DEFAULT_ANSWER_WAIT_MS = 30000
const MAX_ANSWER_WAIT_MS = 45000

let busy = false
// What other players have said since her mind last looked.
const hearing = createHearing({ self: MC_USERNAME })

class BridgeError extends Error {
  constructor (status, code, message) {
    super(message)
    this.status = status
    this.code = code
  }
}

function log (message) {
  console.log(`[${new Date().toISOString()}] ${message}`)
}

function startViewer (theBot) {
  if (VIEWER_PORT === null) return
  try {
    const { mineflayer: viewer } = require('prismarine-viewer')
    viewer(theBot, { port: VIEWER_PORT, firstPerson: false })
    log(`viewer on port ${VIEWER_PORT} (all network interfaces)`)
  } catch (e) {
    log(`viewer not started: ${e.message}`)
  }
}

/** Join the world as her. `onGone(bot)` is called when that bot leaves by itself. */
function login (onGone) {
  return new Promise((resolve, reject) => {
    const theBot = mineflayer.createBot({
      host: MC_HOST, port: MC_PORT, username: MC_USERNAME, auth: 'offline', version: MC_VERSION
    })
    theBot.loadPlugin(pathfinder)
    theBot.loadPlugin(collectBlock)
    const timer = setTimeout(() => {
      theBot.removeAllListeners()
      try { theBot.end() } catch (e) {}
      reject(new BridgeError(503, 'world_unreachable', `No answer from the Minecraft server at ${MC_HOST}:${MC_PORT}.`))
    }, LOGIN_TIMEOUT_MS)
    const fail = reason => {
      clearTimeout(timer)
      reject(new BridgeError(503, 'world_unreachable', `Could not join the Minecraft server: ${reason}`))
    }
    theBot.once('error', err => fail(err.message))
    theBot.once('kicked', reason => fail(`kicked (${JSON.stringify(reason)})`))
    theBot.once('spawn', () => {
      theBot.removeAllListeners('error')
      theBot.removeAllListeners('kicked')
      theBot.on('error', err => log(`bot error: ${err.message}`))
      theBot.on('kicked', reason => log(`kicked: ${JSON.stringify(reason)}`))
      theBot.on('end', reason => {
        log(`left the world (${reason})`)
        onGone(theBot)
      })
      theBot.on('chat', (from, text) => hearing.hear(from, text, false))
      theBot.on('whisper', (from, text) => hearing.hear(from, text, true))
      // Settling in can fail (no chunks, no ticks). That must reject this
      // login, not escape as an unhandled rejection; the watchdog above stays
      // armed until it is done.
      Promise.resolve().then(async () => {
        theBot.pathfinder.setMovements(new Movements(theBot))
        // Health, food and the first chunks arrive just after spawn.
        await theBot.waitForTicks(20)
        startViewer(theBot)
      }).then(() => {
        clearTimeout(timer)
        resolve(theBot)
      }, err => {
        clearTimeout(timer)
        try { theBot.end() } catch (e) {}
        reject(new BridgeError(503, 'world_unreachable', `Joined the world but could not settle in: ${err.message}`))
      })
    })
  })
}

async function leave (theBot) {
  stopMoving(theBot)
  if (theBot.viewer && theBot.viewer.close) {
    try { theBot.viewer.close() } catch (e) {}
  }
  await new Promise(resolve => {
    const timer = setTimeout(resolve, 3000)
    theBot.once('end', () => { clearTimeout(timer); resolve() })
    theBot.quit()
  })
}

const session = createSession({
  login: onGone => login(onGone).then(theBot => {
    log(`joined ${MC_HOST}:${MC_PORT} as ${MC_USERNAME}`)
    return theBot
  }),
  leave
})

/** What she perceives now, with what she has heard since the last look. */
function look (theBot) {
  return { ...observe(theBot), heard: hearing.drain() }
}

function requireSession () {
  if (!session.connected()) throw new BridgeError(409, 'no_session', 'Jenbina is not in the world. Start a session first.')
}

async function act (name, args, budgetMs) {
  requireSession()
  const routine = ACTIONS[name]
  if (!routine) throw new BridgeError(400, 'unknown_action', `There is no action called "${name}".`)
  if (busy) throw new BridgeError(409, 'busy', 'She is already in the middle of something.')
  // Busy until the result has been read, so nothing else starts while pickups settle.
  busy = true
  const theBot = session.bot()
  try {
    const outcome = await runRoutine({
      bot: theBot,
      name,
      routine,
      args,
      budgetMs: Math.min(Math.max(Number(budgetMs) || DEFAULT_BUDGET_MS, 1000), MAX_BUDGET_MS),
      graceMs: OVERRUN_GRACE_MS,
      deps: {
        inventoryCounts,
        observe: look,
        stop: stopMoving,
        disconnect: async gone => { if (session.bot() === gone) await session.end() }
      }
    })
    log(`${name}: ${outcome.ok ? 'ok' : 'not ok'} - ${outcome.summary}`)
    return outcome
  } catch (e) {
    if (e instanceof BridgeError) throw e
    throw new BridgeError(503, 'world_unreachable', `She was cut off from the world during the action: ${e.message}`)
  } finally {
    busy = false
  }
}

/** Whisper one line to another player and wait for what they say back. */
async function say (to, text, waitMs) {
  const line = cleanLine(text)
  if (typeof to !== 'string' || !PLAIN_NAME.test(to) || to === MC_USERNAME || !line) {
    throw new BridgeError(400, 'bad_request', 'A line needs a player to say it to and something to say.')
  }
  requireSession()
  if (busy) throw new BridgeError(409, 'busy', 'She is already in the middle of something.')
  busy = true
  const theBot = session.bot()
  try {
    const result = await sayAndListen({
      hearing,
      whisper: (name, words) => theBot.whisper(name, words),
      isOnline: name => !!theBot.players[name],
      to,
      text: line,
      waitMs: Math.min(Math.max(Number(waitMs) || DEFAULT_ANSWER_WAIT_MS, 1000), MAX_ANSWER_WAIT_MS)
    })
    log(`say to ${to}: ${result.answered ? `answered (${result.heard.length} line(s))` : (result.reason || 'no answer')}`)
    return result
  } finally {
    busy = false
  }
}

function readJson (request) {
  return new Promise((resolve, reject) => {
    let body = ''
    request.on('data', chunk => {
      body += chunk
      if (body.length > 65536) reject(new BridgeError(413, 'too_large', 'Request body too large.'))
    })
    request.on('end', () => {
      if (!body) return resolve({})
      try {
        resolve(JSON.parse(body))
      } catch (e) {
        reject(new BridgeError(400, 'bad_json', 'Request body was not valid JSON.'))
      }
    })
    request.on('error', reject)
  })
}

async function route (request) {
  const path = new URL(request.url, 'http://localhost').pathname
  const key = `${request.method} ${path}`
  if (key === 'GET /health') return { ok: true, connected: session.connected(), version: MC_VERSION }
  if (key === 'POST /session/start') {
    return { ok: true, observation: look(await session.start()) }
  }
  if (key === 'POST /session/end') {
    await session.end()
    return { ok: true }
  }
  if (key === 'GET /observe') {
    requireSession()
    return look(session.bot())
  }
  if (key === 'POST /act') {
    const body = await readJson(request)
    return act(String(body.name || ''), body.args, body.budget_ms)
  }
  if (key === 'POST /say') {
    const body = await readJson(request)
    return say(body.to, body.text, body.wait_ms)
  }
  throw new BridgeError(404, 'not_found', `No such endpoint: ${key}`)
}

const server = http.createServer((request, response) => {
  route(request).then(
    payload => [200, payload],
    error => [error.status || 500, { ok: false, error: error.code || 'internal', message: error.message }]
  ).then(([status, payload]) => {
    if (status >= 500 && !(payload.error === 'world_unreachable')) log(`error: ${payload.message}`)
    response.writeHead(status, { 'content-type': 'application/json' })
    response.end(JSON.stringify(payload))
  })
})

async function shutdown () {
  log('shutting down')
  await session.end().catch(() => {})
  server.close(() => process.exit(0))
  setTimeout(() => process.exit(0), 2000).unref()
}

if (require.main === module) {
  // A stray rejection inside Mineflayer must not take her body down with it.
  process.on('unhandledRejection', reason => log(`unhandled rejection: ${reason && reason.message ? reason.message : reason}`))
  process.on('SIGTERM', shutdown)
  process.on('SIGINT', shutdown)
  // Localhost only: nothing here is authenticated.
  server.listen(BRIDGE_PORT, '127.0.0.1', () => {
    log(`bridge listening on http://127.0.0.1:${BRIDGE_PORT}, world ${MC_HOST}:${MC_PORT} (${MC_VERSION})`)
  })
}

module.exports = { server }
