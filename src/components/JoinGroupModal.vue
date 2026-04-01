<template>
    <div id="modalBackground" @click="closeModal">
        <div id="modalContent" @click.stop>
            <h3>Join {{ groupLeader }}'s Group?</h3>
            <p>Proposed Time of Redemption:</p>
            <p>{{ proposedDateTime }}</p>

            <div id="modalButtons">
                <button id="cancel" @click="closeModal">Cancel</button>
                <button id="join" @click="joinGroup">Join</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        groupId: String,
        groupLeader: String,
        proposedDateTime: String
    },
    methods: {
        closeModal() { // emit event to parent ViewGroup to close modal
            this.$emit('close-modal');
        },
        joinGroup() {
            this.$emit('join-group');  // emit event to parent ViewGroup to handle join group logic
        }
    }
};
</script>

<style scoped>
#modalBackground {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

#modalContent {
    background: #F3F3F3;
    padding: 20px;
    width: 400px;
    height: 200px;
    text-align: center;
    border-radius: 10px;
}

#modalButtons {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
    padding: 0 50px;
    gap: 30px; 
}

#modalButtons button {
    flex: 1; 
    border-radius: 5px;
    border: none;
    padding: 10px 40px;
    font-size: 14px;
    font-weight: 500;
    text-align: center;
}

#modalButtons button:hover {
    cursor: pointer;
}

#join {
    background-color: #ABC6A9;
}

#cancel {
    background-color: #DFC0BE;
}
</style>