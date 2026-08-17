<template>
  <button
    :type="type"
    :class="classes"
    :disabled="disabled"
    :aria-label="ariaLabel"
    :title="title"
    @click="$emit('click', $event)"
  >
    <span v-if="icon" aria-hidden="true">{{ icon }}</span>
    <span v-if="$slots.default" :class="{ label: iconOnly }"><slot /></span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: value => ['primary', 'secondary', 'back', 'voice', 'send'].includes(value)
  },
  size: { type: String, default: '' }, // '' | 'small'
  disabled: { type: Boolean, default: false },
  ariaLabel: { type: String, default: null },
  title: { type: String, default: null },
  icon: { type: String, default: null },
  iconOnly: { type: Boolean, default: false },
  type: { type: String, default: 'button' }
})

defineEmits(['click'])

const variantClass = {
  primary: 'primary-btn',
  secondary: 'secondary-btn',
  back: 'back-btn',
  voice: 'voice-btn',
  send: 'send-btn'
}

const classes = computed(() => [
  variantClass[props.variant],
  props.size ? props.size : null
])
</script>
