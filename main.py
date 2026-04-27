// main.py — Универсальный прокси к Telegram Bot API для Render
import { Context, Hono } from 'hono'
import { cors } from 'hono/cors'

const app = new Hono()
const TELEGRAM_API = "https://api.telegram.org"

// Middleware: CORS для отладки
app.use('*', cors())

// Универсальный обработчик: поддерживает оба формата путей
app.all('/bot:token/:method{.*}', async (c) => {
  const { token, method } = c.req.param()
  // token уже включает и ID, и секрет (через :), т.к. путь /bot8403731624:AAA.../getMe
  
  const targetUrl = `${TELEGRAM_API}/bot${token}/${method}`
  
  try {
    // Копируем заголовки и тело запроса
    const headers = new Headers(c.req.raw.headers)
    headers.set('Host', 'api.telegram.org')
    
    const body = await c.req.raw.clone().text()
    
    const response = await fetch(targetUrl, {
      method: c.req.method,
      headers: headers,
      body: c.req.method !== 'GET' ? body : undefined,
    })
    
    // Возвращаем ответ от Telegram
    const responseText = await response.text()
    return new Response(responseText, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    })
  } catch (error) {
    return c.json({ error: error.message }, 502)
  }
})

// Резервный обработчик для формата aiogram: /<method> с токеном в заголовке или теле
app.all('/:method{.*}', async (c) => {
  const method = c.req.param('method')
  const token = c.req.header('X-Bot-Token') // Опционально: токен в заголовке
  
  if (!token) {
    return c.json({ error: 'Bot token required in X-Bot-Token header or URL path' }, 400)
  }
  
  const targetUrl = `${TELEGRAM_API}/bot${token}/${method}`
  
  try {
    const headers = new Headers(c.req.raw.headers)
    headers.set('Host', 'api.telegram.org')
    headers.delete('X-Bot-Token') // Удаляем наш кастомный заголовок
    
    const body = await c.req.raw.clone().text()
    
    const response = await fetch(targetUrl, {
      method: c.req.method,
      headers: headers,
      body: c.req.method !== 'GET' ? body : undefined,
    })
    
    const responseText = await response.text()
    return new Response(responseText, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    })
  } catch (error) {
    return c.json({ error: error.message }, 502)
  }
})

// Health check
app.get('/health', (c) => c.json({ status: 'ok' }))
app.head('/health', (c) => new Response(null, { status: 200 }))

export default app
