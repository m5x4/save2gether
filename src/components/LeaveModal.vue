<template>
    <div class="popup-overlay">
      <div class="popup leave-popup">
        <h3>Leave Group</h3>
        <p>Are you sure you want to leave this group?</p>
        <div class="leave-actions">
          <button class="cancel-btn" @click="$emit('close')">Cancel</button>
          <button class="confirm-btn" @click="$emit('leave')">Yes, Leave</button>
        </div>
      </div>
    </div>
  </template>

  <style scoped>
  .popup-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
  }
  .popup.leave-popup {
    background: white;
    padding: 20px;
    border-radius: 10px;
    width: 350px;
    text-align: center;
  }
  .leave-actions {
    display: flex;
    justify-content: center;
    margin-top: 20px;
    gap: 20px;
  }
  .cancel-btn {
    background-color: #ccc;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
  }
  .confirm-btn {
    background-color: #d9534f;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
  }
  </style>
  