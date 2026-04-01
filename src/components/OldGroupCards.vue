<template>
    <div id="oldGroupCard">
        <div id="timing">
            <p> {{ proposedDateTime }} </p>
        </div>
        <div id="details">
            <h3> {{ dealName }} </h3>
            <p> {{ groupLeader }}'s Group</p>
            <p> {{ numFilled }}/{{ groupSize }} People</p>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        dealName: String,
        groupLeader: String,
        proposedDateTime: String,
        numFilled: String,
        groupSize: String,
    },
}
</script>

<style scoped>
#oldGroupCard {
    background-color: #f3f3f3;
    border-radius: 15px;
    padding: 10px 40px;
    margin-bottom: 20px;
}

#timing {
    background-color: #D9D9D9;
    color: black;
    border-radius: 5px;
    display: inline-block;
    padding: 0px 10px;
    margin-top: 10px;
}

#timing p {
    margin: 5px 0px;
}

#details h3 {
    margin-bottom: 10px;
}

#details p {
    margin: 5px 0px;
}
</style>