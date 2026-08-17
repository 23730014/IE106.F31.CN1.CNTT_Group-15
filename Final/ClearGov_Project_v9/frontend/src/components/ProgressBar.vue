<template>
  <div class="progress-area">
    <div class="progress-info">
      <span>Bước {{ step }} / {{ total }}</span>
      <span>{{ Math.round(percent) }}%</span>
    </div>
    <div class="progress">
      <div :style="{ width: percent + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  step: { type: Number, required: true },
  total: { type: Number, required: true },
  percent: { type: Number, required: true }
})
</script>
