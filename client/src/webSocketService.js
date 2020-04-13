class WebSocketService {
    static instance = null
    callbacks = {}

    static getInstance() {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService()
        }
        return WebSocketService.instance
    }

    constructor() {
        this.socketRef = null
    }

    async connect() {
        const path = 'ws://localhost:8000/websocket/'
        this.socketRef = new WebSocket(path)

        const sleep = (ms) => {
            return new Promise(resolve => setTimeout(resolve, ms))
        }

        let timeToConnect = 0
        while (this.socketRef.readyState !== this.socketRef.OPEN) {
            await sleep(1)
            ++timeToConnect
        }

        console.log('The WebSocket took ' + timeToConnect + ' milliseconds to connect.')

        this.socketRef.onmessage = e => {
            this.socketNewMessage(e.data)
        }

        this.socketRef.onopen = () => {
            console.log("WebSocket open")
        }

        this.socketRef.onerror = e => {
            console.log(e.message)
        }

        this.socketRef.onclose = () => {
            console.log("WebSocket closed, restarting..")
            this.connect()
        }
    }

    socketNewMessage(data) {
        const parsedData = JSON.parse(data)
        const command = parsedData.command
        if (Object.keys(this.callbacks).length === 0) {
            return
        }

        if(command === 'fetch_arms'){
            console.log("WebSocketService -> socketNewMessage -> parsedData", parsedData)
            this.callbacks[command](parsedData.arms)
        }
    }

    fetchArms() {
        this.sendMessage({ command: 'fetch_arms' })
    }

    fetchMessages(username) {
        this.sendMessage({ command: 'fetch_messages', username: username })
    }

    newChatMessage(message) {
        this.sendMessage({ command: 'new_message', from: message.from, text: message.text })
    }

    addCallbacks(callbacks) {
        callbacks.forEach(callback => this.callbacks[callback.command] = callback.fn)
    }

    sendMessage(data) {
        try {
            console.log({ ...data })
            this.socketRef.send(JSON.stringify({ ...data }))
        }
        catch (err) {
            console.log(err.message)
        }
    }

    state() {
        return this.socketRef.readyState
    }

    waitForSocketConnection(callback) {
        const socket = this.socketRef
        const recursion = this.waitForSocketConnection
        setTimeout(
            function () {
                if (socket.readyState === 1) {
                    console.log("Connection to Websocket Server is established")
                    if (callback != null) {
                        callback()
                    }
                    return
                }
                else {
                    console.log("Waiting for connection...")
                    recursion(callback)
                }
            }, 1
        )
    }
}

let WebSocketInstance = WebSocketService.getInstance()

export default WebSocketInstance