<template>
  <Header></Header>
  <div id="body">
    <h2>{{ dealName }}</h2>
    <p>{{ dealLocation }}</p>

    <!-- Create Group Section -->
    <CreateGroupButton :dealId="dealId" :dealName="dealName" />

    <!-- View Group Section -->
    <div id="viewGroup">
      <div v-if="groups.length === 0" id="noGroups">No groups available</div>
      <div v-else id="groupsContainer">
        <GroupCard
          v-for="group in groups"
          :key="group.id"
          :groupId="group.id"
          :groupLeader="group.leader"
          :groupLeaderId="group.leaderId"
          :createdDateTime="timeAgo(group.createdDateTime)"
          :proposedDateTime="formatDate(group.proposedDateTime)"
          :numFilled="group.numFilled"
          :groupSize="this.groupSize"
          :leaderRating="group.leaderRating"
          :leaderProfilePic="group.leaderProfilePic"
          @show-modal="displayModal"
        />
      </div>
    </div>

    <!-- Group Modal -->
    <JoinGroupModal
      v-if="isModalVisible"
      :groupId="modalData.groupId"
      :groupLeader="modalData.groupLeader"
      :proposedDateTime="modalData.proposedDateTime"
      @close-modal="closeModal"
      @join-group="joinGroup"
    />
  </div>
</template>

<script>
import { auth } from "@/firebase/firebase.js";
import {
  getUser,
  getGroups,
  getGroupById,
  getGroupMembers,
  getGroupMemberById,
  getDeal,
  addUserToGroup,
  getReviews,
} from "@/firebase/firestore.js";
import GroupCard from "@/components/GroupCard.vue";
import JoinGroupModal from "@/components/JoinGroupModal.vue";
import CreateGroupButton from "@/components/CreateGroupButton.vue";
import Header from "@/components/Header.vue";

export default {
  data() {
    return {
      // form
      showForm: false,
      formData: {
        date: "",
        time: "",
        groupSize: "",
      },
      userData: null,
      // view groups
      dealId: "",
      dealName: "",
      dealLocation: "",
      groupSize: "",
      groups: [],

      // modal data
      isModalVisible: false,
      modalData: {
        groupId: "",
        groupLeader: "",
        proposedDateTime: "",
      },
    };
  },
  components: {
    GroupCard,
    JoinGroupModal,
    CreateGroupButton,
    Header,
  },
  async created() {
    // Get current user
    const user = auth.currentUser;
    if (user) {
      // Fetch user data from Firestore
      this.userData = await getUser(user.uid);
    }
    // for view groups
    this.dealId = this.$route.query.dealId;
    await this.fetchDealInfo();
    await this.fetchGroups();
  },

  methods: {
    // fetch deal info
    async fetchDealInfo() {
      try {
        const dealDetails = await getDeal(this.dealId);
        this.dealName = dealDetails.dealName;
        this.dealLocation = dealDetails.location;
        this.groupSize = `${dealDetails.numRequired}`;
      } catch (error) {
        console.error("Error fetching deal:", error);
      }
    },
    // view groups
    async fetchGroups() {
      try {
        // fetch the group doc ids
        const fetchedGroups = await getGroups(this.dealId);
        // fetch deal data to get group size
        const dealDetails = await getDeal(this.dealId);
        const groupSize = `${dealDetails.numRequired}`;

        // from group ids, get all the additional info
        const groupDataPromises = fetchedGroups.map(async (group) => {
          // from each group id, fetch the group info(createdDateTime, isFull, proposedDateTime)
          const groupDetails = await getGroupById(this.dealId, group.id);
          // set as null for those group that are already full to not display
          if (groupDetails.isFull) {
            return null;
          }
          // set a null for groups that are closed
          if (groupDetails.isClosed) {
            return null;
          }
          // from each group id, access the group member subcollection and get the group member docs
          const groupMembersData = await getGroupMembers(this.dealId, group.id);
          // get each group member info
          const groupMembers = await Promise.all(
            groupMembersData.map(async (member) => {
              // from each group member doc, access the member info (isLeader, joinDateTime, user ref)
              const memberDetails = await getGroupMemberById(
                this.dealId,
                group.id,
                member.id
              );
              return memberDetails;
            })
          );

          // Find leader amongst member, return me the leader doc
          const leader = groupMembers.find((member) => member.isLeader);

          // Fetch the leader info (firstName, lastName)
          let leaderDetails = null;
          let leaderRating = 0;
          if (leader && leader.user) {
            const userRef = leader.user;
            // get the leader info
            const userDetails = await getUser(userRef.id);
            leaderDetails = userDetails;
            // fetch rating for leader
            const reviews = await getReviews(leaderDetails.id);
            if (reviews.length > 0) {
              const totalRating = reviews.reduce(
                (sum, review) => sum + review.rating,
                0
              );
              leaderRating = parseFloat(
                (totalRating / reviews.length).toFixed(1)
              );
            }
          }

          // Return the complete group information
          return {
            ...group,
            groupId: group.id,
            createdDateTime: groupDetails.createdDateTime,
            proposedDateTime: groupDetails.proposedDateTime,
            numFilled: groupMembers.length.toString(), // The number of group members
            groupSize: groupSize, // Group size from group details
            leader: leaderDetails
              ? `${leaderDetails.firstName} ${leaderDetails.lastName}`
              : "Unknown Leader",
            leaderId: leaderDetails
              ? `${leaderDetails.id}`
              : "Unknown Leader ID",
            leaderRating,
            leaderProfilePic: leaderDetails
              ? leaderDetails.profilePicURL
              : "/src/assets/avatar.png",
          };
        });

        // Wait for all the group data to be processed, filtering out groups already filled
        this.groups = (await Promise.all(groupDataPromises)).filter(
          (group) => group !== null
        );
      } catch (error) {
        console.error("Error fetching groups:", error);
      }
    },

    formatDate(timestamp) {
      try {
        const date = new Date(timestamp.seconds * 1000);
        const formattedDate = date.toLocaleString("en-SG", {
          day: "2-digit",
          month: "2-digit",
          year: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        });
        return formattedDate;
      } catch (error) {
        console.error("There is an error converting time: ", error);
        return "System unable to fetch Date";
      }
    },

    timeAgo(timestamp) {
      try {
        const now = new Date();
        const createdTime = new Date(timestamp.seconds * 1000);
        const diffInSeconds = Math.floor((now - createdTime) / 1000);

        if (diffInSeconds < 60) {
          return "Just now";
        }
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) {
          return `${diffInMinutes} minute${diffInMinutes > 1 ? "s" : ""} ago`;
        }
        const diffInHours = Math.floor(diffInSeconds / 3600);
        if (diffInHours < 24) {
          return `${diffInHours} hour${diffInHours > 1 ? "s" : ""} ago`;
        }
        const diffInDays = Math.floor(diffInSeconds / 86400);
        return `${diffInDays} day${diffInDays > 1 ? "s" : ""} ago`;
      } catch (error) {
        console.error("Error calculating time ago:", error);
        return "Unable to fetch time";
      }
    },

    // modal methods
    displayModal(modalData) {
      // pass in data emitted from group card when show-modal event emitted
      this.modalData = modalData;
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
    },
    async joinGroup() {
      try {
        await addUserToGroup(
          this.dealId,
          this.modalData.groupId,
          this.userData
        );
        this.closeModal();

        // get chat id
        const groupDetails = await getGroupById(
          this.dealId,
          this.modalData.groupId
        );
        if (groupDetails && groupDetails.chatRef) {
          const chatId = groupDetails.chatRef.id;
          // Redirect to chat page
          this.$router.push({ path: "/chat", query: { chatId: chatId } });
        } else {
          console.error("Chat reference not found for this group.");
          await this.fetchGroups();
        }
      } catch (error) {
        console.error("Error joining group:", error);
      }
    },
  },
};
</script>

<style>
#body {
  align-items: left;
  margin-left: 60px;
  margin-right: 60px;
}
</style>
