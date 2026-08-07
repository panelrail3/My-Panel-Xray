<script setup>
import {onMounted,ref} from "vue"; import axios from "axios"
const items=ref([]); const headers=()=>({Authorization:`Bearer ${localStorage.token}`})
const form=ref({name:"xhttp-tls",transport:"xhttp",security:"tls",listen_port:443,path:"/xhttp"})
async function load(){items.value=(await axios.get("/api/inbounds",{headers:headers()})).data}
async function add(){await axios.post("/api/inbounds",form.value,{headers:headers()});load()}
onMounted(load)
</script>
<template><div class="card"><h1>Inbounds</h1><input v-model="form.name"><select v-model="form.transport"><option>raw</option><option>xhttp</option><option>websocket</option><option>grpc</option></select><select v-model="form.security"><option>none</option><option>tls</option><option>reality</option></select><button @click="add">Create</button><pre>{{items}}</pre></div></template>
