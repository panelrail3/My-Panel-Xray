<script setup>
import {onMounted,ref} from "vue"; import axios from "axios"
const users=ref([]); const name=ref("")
const headers=()=>({Authorization:`Bearer ${localStorage.token}`})
async function load(){users.value=(await axios.get("/api/users",{headers:headers()})).data}
async function add(){await axios.post("/api/users",{username:name.value},{headers:headers()});name.value="";load()}
onMounted(load)
</script>
<template><div class="card"><h1>Users</h1><input v-model="name" placeholder="username"><button @click="add">Create</button><table><tr v-for="u in users" :key="u.id"><td>{{u.username}}</td><td>{{u.uuid}}</td><td>{{u.enabled}}</td></tr></table></div></template>
