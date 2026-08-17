<template>
  <div
    v-if="text"
    :class="variant === 'error' ? 'upload-error' : 'ocr-status'"
    :role="variant === 'error' ? 'alert' : 'status'"
    :aria-live="variant === 'error' ? undefined : 'polite'"
  >
    <span v-if="variant === 'error'" aria-hidden="true">⚠️ </span>{{ text }}
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'info', // 'info' | 'error'
    validator: value => ['info', 'error'].includes(value)
  },
  text: { type: String, default: '' }
})
</script>
