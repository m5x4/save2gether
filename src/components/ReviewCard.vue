<template>
    <div id="reviewCard">
        <div id="userInfo">
            <h3 id="name">{{ reviewerName }}</h3>
            <div id="stars">
                <span v-for="index in 5" :key="index" id="starIcon">
                    <component :is="getStarComponent(index)" />
                </span>
            </div>
        </div>
        <div id="contentInfo">
            <p id="content">{{ content }}</p>
        </div>
    </div>
</template>

<script>
import EmptyStar from '@/assets/icons/EmptyStar.vue';
import FullStar from '@/assets/icons/FullStar.vue';
import HalfStar from '@/assets/icons/HalfStar.vue';

export default {
    props: {
        reviewerName: String,
        content: String,
        rating: Number
    },
    components: {
        FullStar,
        HalfStar,
        EmptyStar,
    },
    methods: {
        getStarComponent(index) {
            if (this.rating >= index) return 'FullStar'
            if (this.rating >= index - 0.5) return 'HalfStar'
            return 'EmptyStar'
        }
    }
}
</script>

<style scoped>
#reviewCard {
    background-color: #f3f3f3;
    border-radius: 15px;
    padding: 10px 40px;
    margin-bottom: 20px;
}

#userInfo {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-top: 10px;
    margin-bottom: 10px;
}

#name {
    margin: 0;
}

#content {
    margin: 5px 0;
}

#stars {
    padding-top: 5px;
}

#starIcon {
    width: 20px;
    height: 20px;
    display: inline-block;
    margin-right: 2px;
}
</style>