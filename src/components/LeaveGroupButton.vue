<template>
  <button class="leave-btn" @click="handleClick">Leave Group</button>
</template>

<script>
export default {
  name: 'LeaveGroupButton',
  methods: {
    handleClick() {
      this.$emit('leave');
    }
  }
}
</script>

<style scoped>
.leave-btn {
  background-color: #DFC0BE;
  border-radius: 10px;
  border: none;
  padding: 10px 15px;
  font-family: serif;
  cursor: pointer;
}
</style> 