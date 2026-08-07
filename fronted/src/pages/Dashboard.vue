<script setup>
import {onMounted,ref} from "vue"; import axios from "axios"
const token=localStorage.token; const h={Authorization:`Bearer ${token}`}; const health=ref({}); const cap=ref({}); const stats=ref({users:{}})
async function load(){
 try{health.value=(await axios.get("/api/health")).data}catch{}
 try{cap.value=(await axios.get("/api/system/capabilities",{headers:h})).data}catch{}
 try{stats.value=(await axios.get("/api/stats",{headers:h})).data}catch{}
}
onMounted(load)
</script>
<template><div>
<div class="card"><h1>Dashboard</h1><p>Health: {{health.status}}</p><p>Database: {{health.database}}</p><p>Xray: {{health.xray}}</p></div>
<div class="card"><h2>Railway</h2><p>Environment: {{cap.environment}}</p><p>Public: {{cap.public_domain||"—"}}</p><p>TCP Proxy: {{cap.tcp_proxy ? cap.tcp_proxy_domain+":"+cap.tcp_proxy_port : "Disabled"}}</p><p>Volume: {{cap.volume_mount_path||"—"}}</p></div>
<div class="card"><h2>User Traffic</h2><table><tr><th>User</th><th>Up</th><th>Down</th><th>Total</th></tr><tr v-for="(v,k) in stats.users" :key="k"><td>{{k}}</td><td>{{v.uplink}}</td><td>{{v.downlink}}</td><td>{{v.total}}</td></tr></table></div>
</div></template>
