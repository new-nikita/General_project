import { defineStore } from "pinia"

export interface Message {
  id?: number
  text: string
  is_self: boolean
  created_at?: string
}

export const useChatStore = defineStore("chatStore", {
  state: () => ({
    messages: [] as Message[],
    connected: false,
  }),
  actions: {
    addMessage(msg: Message) {
      this.messages.push(msg)
    },
    setMessages(msgs: Message[]) {
      this.messages = msgs
    },
    setConnected(value: boolean) {
      this.connected = value
    },
  },
})