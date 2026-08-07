<script setup>
import {ref,onMounted} from "vue"; import axios from "axios"
const users=ref([]), result=ref(null); const h={Authorization:`Bearer ${localStorage.token}`}
onMounted(async()=>users.value=(await axios.get("/api/users",{headers:h})).data)
async function make(id){result.value=await axios.post("/api/subscriptions/"+id,{}, {headers:h})}
</script>
<template><div class="card"><h1>Subscriptions</h1><div v-for="u in users" :key="u.id"><button @click="make(u.id)">Create for {{u.username}}</button></div><pre>{{result}}</pre></div></template>
