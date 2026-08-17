<template>
  <a class="support-btn" :href="`tel:${phone}`" :aria-label="`Gọi hỗ trợ qua điện thoại, số ${displayPhone}`">
    <span aria-hidden="true">☎</span>
    <span class="label">Gọi hỗ trợ</span>
  </a>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  phone: { type: String, default: '19001111' }
})

const displayPhone = computed(() =>
  props.phone.replace(/(\d{4})(\d{4})/, '$1 $2')
)
</script>
