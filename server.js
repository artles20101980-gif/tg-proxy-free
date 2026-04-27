// server.js
import { serve } from '@hono/node-server'
import app from './main.js'

const port = process.env.PORT || 10000
console.log(`🚀 Server running on port ${port}`)

serve({
  fetch: app.fetch,
  port: port
})
