import ReconnectingWebSocket from 'reconnecting-websocket'

class WebSocketService {
  static instance = null
  callbacks = {}
  autoReconnectInterval = 1000

  static getInstance() {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService()
    }
    return WebSocketService.instance
  }

  constructor() {
    this.socket = null
  }

  addCallbacks(callbacks) {
    callbacks.forEach(callback => this.callbacks[callback.command] = callback.fn)
  }


  waitForSocketConnection = (callback) => {
    const socket = this.socket
    const recursion = this.waitForSocketConnection
    setTimeout(
      () => {
        if (socket?.readyState === 1) {
          if (callback != null) callback()
          return
        } else {
          recursion(callback)
        }
      },
    1)
  }

  connect() {
    const path = process.env.NODE_ENV === 'development' ? 'ws://localhost:8000/websocket/' : `ws://${window.location.host}:80/websocket/`

    // Avoid making a duplicate connection if another component started it already
    if (this.socket !== null) return

    this.socket = new ReconnectingWebSocket(path)

    this.socket.onmessage = e => {
      this.onNewMessage(e.data)
    }

    this.socket.onopen = () => {
      console.log('WebSocket connection open!')
    }

    this.socket.onclose = () => {
      console.log('WebSocket connection closed, trying to reconnect...')
    }
  }

  // Send Messages
  sendMessage(data) {
    try {
      this.socket.send(JSON.stringify({ ...data }))
    }
    catch (err) {
      console.log(err.message)
    }
  }

  // Receive Messages
  onNewMessage(data) {
    const parsedData = JSON.parse(data)
    if (Object.keys(this.callbacks).length === 0) return
    this.callbacks[parsedData.command](parsedData)
  }
}

export default WebSocketService.getInstance()