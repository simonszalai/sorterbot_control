class WebSocketService {
    static instance = null

    static getInstance() {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService()
        }
        return WebSocketService.instance
    }

    constructor() {
        this.socket = null
        this.callbacks = {}
    }

    async connect() {
        const path = 'ws://localhost:8000/websocket/'
        this.socket = new WebSocket(path)

        const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

        let timeToConnect = 0
        while (this.socket.readyState !== this.socket.OPEN) {
            await sleep(1)
            ++timeToConnect
        }
        console.log('The WebSocket took ' + timeToConnect + ' milliseconds to connect.')

        this.socket.onmessage = e => {
            this.onNewMessage(e.data)
        }

        this.socket.onopen = () => {
            console.log("WebSocket connection open!")
        }

        this.socket.onerror = e => {
            console.log(e.message)
        }

        this.socket.onclose = () => {
            console.log("WebSocket closed, restarting..")
            this.connect()
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
    }

    addCallbacks(callbacks) {
        callbacks.forEach(callback => this.callbacks[callback.command] = callback.fn)
    }
}

export default WebSocketService.getInstance()