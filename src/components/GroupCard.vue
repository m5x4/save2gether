<template>
	<div id="GroupCard">
		<div id="GroupInfo">
			<h3 id="title">{{ groupLeader }}'s Group</h3>
			<div id="UserInfo" @click="goToProfile">
				<img id ="profilePic" :src="leaderProfilePic" alt="User Profile Picture" class="user-icon" />
				<div id="UserInfoDetails">
					<div id="nameRating">
						<p id="Username">{{ groupLeader }}</p>
						<div id="stars">
							<span v-for="index in 5" :key="index" id="starIcon">
								<component :is="getStarComponent(index)" />
							</span>
						</div>
					</div>
					<p id="CreatedTime">Created {{ createdDateTime }}</p>
				</div>
				<span class="tooltip">Click here to view {{ groupLeader }}'s profile!</span>
			</div>
		</div>
		<div id="GroupDetails">
			<h3 id="ProposedTime">Proposed time: {{ proposedDateTime }}</h3>
			<h3 id="GroupSize">{{ numFilled }}/{{ groupSize }} Filled</h3>
			<button id="join" @click="displayModal">Join Group</button>
		</div>
	</div>
</template>

<script>
import EmptyStar from '@/assets/icons/EmptyStar.vue';
import FullStar from '@/assets/icons/FullStar.vue';
import HalfStar from '@/assets/icons/HalfStar.vue';

export default {
	props: {
		dealId: String,
		groupId: String,
		groupLeader: String,
		groupLeaderId: String,
		createdDateTime: String,
		proposedDateTime: String,
		numFilled: String,
		groupSize: String,
		leaderRating: Number,
		leaderProfilePic: String,
	},

	components: {
		FullStar,
		HalfStar,
		EmptyStar,
	},

	methods: {
		displayModal() {
			// emit event to parent ViewGroup to show modal
			this.$emit("show-modal", {
				groupId: this.groupId,
				groupLeader: this.groupLeader,
				proposedDateTime: this.proposedDateTime,
			});
		},
		goToProfile() {
			this.$router.push(`/ProfilePage/${this.groupLeaderId}`);
		},

		getStarComponent(index) {
			if (this.leaderRating >= index) return 'FullStar'
			if (this.leaderRating >= index - 0.5) return 'HalfStar'
			return 'EmptyStar'
		}
	},
};
</script>

<style scoped>
#GroupCard {
	background-color: #f3f3f3;
	border-radius: 15px;
	padding: 20px 40px;
	margin-bottom: 20px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

#GroupInfo {
	display: flex;
	flex-direction: column;
}

#UserInfo {
	display: flex;
	align-items: center;
	gap: 15px;
	margin-bottom: 5px;
}

#UserInfo p {
	margin: 5px 0px;
}

#title {
	margin-top: 0px;
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

#GroupDetails {
	text-align: right;
}

.user-icon {
	width: 70px;
	height: 70px;
}

#profilePic {
	width: 50px;
	height: 50px;
}

#join {
	flex: 1;
	border-radius: 5px;
	border: none;
	padding: 8px 25px;
	font-size: 14px;
	font-weight: 500;
	text-align: center;
	background-color: #17334b;
	color: white;
}

#join:hover {
	cursor: pointer;
}

.tooltip {
	visibility: hidden;
	width: max-content;
	background-color: rgba(0, 0, 0, 0.75);
	color: #fff;
	text-align: center;
	border-radius: 5px;
	padding: 5px 10px;
	position: absolute;
	z-index: 10;
	bottom: -30px;
	left: 0;
	opacity: 0;
	transition: opacity 0.3s;
	font-size: 0.9em;
}

#UserInfo {
	position: relative;
	cursor: pointer;
}

#UserInfo:hover .tooltip {
	visibility: visible;
	opacity: 1;
}

#nameRating {
	display: flex;
	align-items: center;
	gap: 20px;
}
</style>
