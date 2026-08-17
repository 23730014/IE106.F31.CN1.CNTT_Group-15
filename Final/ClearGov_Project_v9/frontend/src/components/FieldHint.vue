<template>
  <p class="field-hint">
    <span aria-hidden="true">💡</span> {{ text }}
  </p>
</template>

<script setup>
defineProps({
  text: { type: String, required: true }
})
</script>
