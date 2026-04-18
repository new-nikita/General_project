// frontend/src/router/index.ts
import { createRouter, createWebHistory } from "vue-router"
import MainLayout from "@/layouts/MainLayout.vue"

import Users from "@/views/users/Users.vue"
import Profile from "@/views/users/Profile.vue"
import Login from "@/views/users/Login.vue"
import Register from "@/views/users/Register.vue"
import ChatDialog from "@/views/chat/ChatDialog.vue"
import DialogsList from "@/views/chat/DialogsList.vue"
import ConfirmEmail from "@/views/info/ConfirmEmail.vue"
import ErrorPage from "@/views/info/ErrorPage.vue"

const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", name: "home", component: Users },
      { path: "chat/:id", name: "chat", component: ChatDialog, props: true },
    ],
  },
  { path: "/messages", name: "dialogs", component: DialogsList },
  { path: "/profile/:id", component: Profile },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/confirm-email", component: ConfirmEmail },
  { path: "/error", component: ErrorPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
