<template>
  <div :class="['message-row', role]">
    <div v-if="role === 'bot'" class="avatar" aria-hidden="true">🤖</div>
    <div class="bubble">{{ text }}</div>
  </div>
</template>

<script setup>
defineProps({
  role: {
    type: String,
    required: true,
    validator: value => ['bot', 'user'].includes(value)
  },
  text: { type: String, required: true }
})
</script>
