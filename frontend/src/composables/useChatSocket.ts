import { useChatStore } from "@/stores/chatStore"

export function useChatSocket(dialogId: number) {

  const store = useChatStore()

  let socket: WebSocket | null = null
  let reconnectTimer: number | null = null

  function connect() {

    socket = new WebSocket(
      `ws://${window.location.host}/ws/chat/dialog/${dialogId}`
    )

    socket.onopen = () => {
      store.setConnected(true)
      console.log("chat connected")
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      store.addMessage(data)
    }

    socket.onclose = () => {

      store.setConnected(false)

      reconnectTimer = window.setTimeout(() => {
        connect()
      }, 3000)

    }

  }

  function send(text: string) {

    socket?.send(
      JSON.stringify({ text })
    )

    // optimistic message
    store.addMessage({
      text,
      is_self: true
    })

  }

  function disconnect() {
    socket?.close()
  }

  connect()

  return {
    send,
    disconnect
  }

}