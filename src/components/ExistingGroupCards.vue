<template>
    <div id="existingGroupCard">
        <div id="dealInfo">
            <div id="timing">
                <p> Ongoing Deal: {{ proposedDateTime }} </p>
            </div>
            <div id="remainTiming">
                <p> in {{ remainingTime }} </p>
            </div>
        </div>
        <div id="details">
            <h3> {{ dealName }} </h3>
            <p> {{ groupLeader }}'s Group </p>
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
        remainingTime: String,
    },
}
</script>

<style scoped>
#existingGroupCard {
    background-color: #f3f3f3;
    border-radius: 15px;
    padding: 10px 40px;
    margin-bottom: 20px;
}

#dealInfo {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-top: 10px;
}

#remainTiming {
    color: #818181;
    font-style: italic;
}

#timing {
    background-color: #17334B;
    color: white;
    border-radius: 5px;
    display: inline-block;
    padding: 0px 10px;
}
#dealInfo p {
    margin: 5px 0px;
}

#details h3 {
    margin-top: 10px;
    margin-bottom: 10px;
}

#details p {
    margin: 5px 0px;
}
</style>