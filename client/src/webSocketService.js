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

  addCallbacks(componentName, callbacks) {
    callbacks.forEach(callback => this.callbacks[callback.command] = callback.fn)
    console.log(`Callbacks for '${componentName}' added successfully!`)
  }


  waitForSocketConnection = (componentName, callback) => {
    const socket = this.socket
    const recursion = this.waitForSocketConnection
    setTimeout(
      () => {
        if (socket?.readyState === 1) {
          console.log(`Initial functions for '${componentName}' executed successfully!`)
          if (callback != null) callback()
          return
        } else {
          recursion(componentName, callback)
        }
      },
    1)
  }

  connect() {
    const path = 'ws://localhost:8000/websocket/'

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

  fetchArms() {
    this.sendMessage({ command: 'fetch_arms' })
  }

  getCloudStatus() {
    this.sendMessage({ command: 'cloud_status' })
  }

  startCloud() {
    this.sendMessage({ command: 'cloud_start' })
  }

  stopCloud() {
    this.sendMessage({ command: 'cloud_stop' })
  }

  startSession(armId) {
    this.sendMessage({
      command: 'start_session',
      armId: armId
    })
  }


  // Receive Messages
  onNewMessage(data) {
    const parsedData = JSON.parse(data)
    const command = parsedData.command
    if (Object.keys(this.callbacks).length === 0) return

    if (command === 'fetch_arms') {
      this.callbacks[command](parsedData.arms)
    }
    if (command === 'cloud_status') {
      this.callbacks[command](parsedData.status)
    }
    if (command === 'cloud_start') {
      this.callbacks[command](parsedData.publicIp)
    }
    if (command === 'cloud_stop') {
      this.callbacks[command]()
    }
    if (command === 'arm_conn_status') {
      this.callbacks[command](parsedData.armId, parsedData.cloudConnectSuccess)
    }
  }

  sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))
}

export default WebSocketService.getInstance()