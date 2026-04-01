import { db } from "./firebase.js";
import {
  collection,
  getDocs,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  getDoc,
  arrayUnion,
  arrayRemove,
  query,
  orderBy,
  limit,
  where,
  onSnapshot,
} from "firebase/firestore";

// -------------------- User Collection --------------------

const userCollection = collection(db, "User");

/*
Fields:
- userID: string
- firstName: string
- lastName: string
- profilePicURL: string
- joinDateTime: timestamp
- chats: array of chat references
- deals: array of deal references
- Review: subcollection
*/

// Fetch all users
export const getUsers = async () => {
  const snapshot = await getDocs(userCollection);
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
};

// Fetch a single user by ID
export const getUser = async (userID) => {
  try {
    const userRef = doc(userCollection, userID);
    const userSnap = await getDoc(userRef);
    if (userSnap.exists()) {
      return { id: userSnap.id, ...userSnap.data() };
    } else {
      // console.log("No such user!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching user:", error);
    return null;
  }
};

// Add a new user
export const addUser = async (firstName, lastName, profilePicURL) => {
  try {
    const userRef = await addDoc(userCollection, {
      firstName,
      lastName,
      profilePicURL,
      joinDateTime: new Date(),
      chats: [], // Initialize empty chats array
      deals: [], // Initialize empty deals array
    });
    // console.log(`User ${firstName} ${lastName} added successfully!`);
    return userRef;
  } catch (error) {
    console.error("Error adding user to Firestore:", error);
    throw error;
  }
};

// Update user details
export const updateUser = async (
  userID,
  firstName,
  lastName,
  profilePicURL
) => {
  try {
    const userRef = doc(userCollection, userID);
    await updateDoc(userRef, {
      firstName,
      lastName,
      profilePicURL,
      // Don't update chats/deals array here as it should be managed separately
    });
    // console.log(`User ${firstName} ${lastName} updated successfully!`);
  } catch (error) {
    console.error("Error updating user in Firestore:", error);
    throw error;
  }
};

// Delete a user
export const deleteUser = async (userID) => {
  try {
    const userRef = doc(userCollection, userID);
    await deleteDoc(userRef);
    // console.log(`User with ID ${userID} deleted successfully!`);
  } catch (error) {
    console.error("Error deleting user from Firestore:", error);
    throw error;
  }
};

// Add a chat to user's chats array
export const addChatToUser = async (userId, chatRef) => {
  try {
    const userRef = doc(userCollection, userId);
    await updateDoc(userRef, {
      chats: arrayUnion(chatRef), // Use arrayUnion to add the chat reference
    });
    // console.log(`Chat added to user ${userId}'s chats array`);
  } catch (error) {
    console.error("Error adding chat to user in Firestore:", error);
    throw error;
  }
};

// Remove a chat from user's chats array
export const removeChatFromUser = async (userId, chatId) => {
  try {
    const userRef = doc(userCollection, userId);
    const chatRef = doc(chatCollection, chatId);
    await updateDoc(userRef, {
      chats: arrayRemove(chatRef), // Use arrayRemove to remove the chat reference
    });
    // console.log(`Chat removed from user ${userId}'s chats array`);
  } catch (error) {
    console.error("Error removing chat from user in Firestore:", error);
    throw error;
  }
};

// Get all chats for a user
export const getUserChats = async (userId) => {
  try {
    const userRef = doc(userCollection, userId);
    const userSnap = await getDoc(userRef);
    if (userSnap.exists()) {
      const chatRefs = userSnap.data().chats || [];
      // console.log("chatRefs: ", chatRefs);
      return chatRefs.map((ref) => {
        const parts = ref.path.split("/");
        return parts[1];
      });
    }
    return [];
  } catch (error) {
    console.error("Error fetching user chats:", error);
    return [];
  }
};

// Add a deal to user's deals array
export const addDealToUser = async (userId, dealRef) => {
  try {
    const userRef = doc(userCollection, userId);
    await updateDoc(userRef, {
      deals: arrayUnion(dealRef), // Use arrayUnion to add the deal reference
    });
    // console.log(`Deal added to user ${userId}'s deals array`);
  } catch (error) {
    console.error("Error adding deal to user in Firestore:", error);
    throw error;
  }
};

// Remove a deal from user's deals array
export const removeDealFromUser = async (userId, dealId) => {
  try {
    const userRef = doc(userCollection, userId);
    const dealRef = doc(dealCollection, dealId);
    await updateDoc(userRef, {
      deals: arrayRemove(dealRef), // Use arrayRemove to remove the deal reference
    });
    // console.log(`Deal removed from user ${userId}'s deals array`);
  } catch (error) {
    console.error("Error removing deal from user in Firestore:", error);
    throw error;
  }
};

// Get all deals a user is in
export const getUserDeals = async (userId) => {
  try {
    const userRef = doc(userCollection, userId);
    const userSnap = await getDoc(userRef);
    if (userSnap.exists()) {
      return userSnap.data().deals || [];
    }
    return [];
  } catch (error) {
    console.error("Error fetching user deals:", error);
    return [];
  }
};

// -------------------- Review Subcollection --------------------

/*
Fields:
- reviewID: string
- reviewerRef: reference
- content: string
- rating: number
*/

// Fetch all reviews from a user
export const getReviews = async (userId) => {
  try {
    const reviewsCollection = collection(db, "User", userId, "Review");
    const snapshot = await getDocs(reviewsCollection);
    return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error("Error fetching reviews:", error);
    return [];
  }
};

// Fetch a single review by ID from a user
export const getReviewById = async (userId, reviewId) => {
  try {
    const reviewRef = doc(db, "User", userId, "Review", reviewId);
    const reviewSnap = await getDoc(reviewRef);
    if (reviewSnap.exists()) {
      return { id: reviewSnap.id, ...reviewSnap.data() };
    } else {
      // console.log("No such review!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching review:", error);
  }
};

// Add a new review
export const addReview = async (userId, reviewerRef, content, rating) => {
  try {
    const reviewsCollection = collection(db, "User", userId, "Review");
    const reviewRef = await addDoc(reviewsCollection, {
      reviewerRef,
      content,
      rating,
      createdDateTime: new Date(),
    });
    // console.log(`Review added successfully with ID: ${reviewRef.id}`);
    return reviewRef;
  } catch (error) {
    console.error("Error adding review to Firestore:", error);
    throw error;
  }
};

// Update review details
export const updateReview = async (
  userId,
  reviewId,
  reviewerRef,
  content,
  rating
) => {
  try {
    const reviewRef = doc(db, "User", userId, "Review", reviewId);
    await updateDoc(reviewRef, {
      reviewerRef,
      content,
      rating,
    });
    // console.log(`Review ${reviewId} updated successfully!`);
  } catch (error) {
    console.error("Error updating review in Firestore:", error);
    throw error;
  }
};

// Delete a review
export const deleteReview = async (userId, reviewId) => {
  try {
    const reviewRef = doc(db, "User", userId, "Review", reviewId);
    await deleteDoc(reviewRef);
    // console.log(`Review ${reviewId} deleted successfully!`);
  } catch (error) {
    console.error("Error deleting review from Firestore:", error);
    throw error;
  }
};

// -------------------- Deal Collection --------------------

const dealCollection = collection(db, "Deal");

/*
Fields:
- dealID: string
- merchantName: string
- dealName: string
- category: string
- location: string
- numRequired: number
- postedBy: reference
- createdDateTime: timestamp
- validUntil: timestamp
- Group: subcollection
*/

// Fetch all deals
export const getDeals = async () => {
  const snapshot = await getDocs(dealCollection);
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
};

// Fetch a single deal by ID
export const getDeal = async (dealID) => {
  try {
    const dealRef = doc(dealCollection, dealID);
    const dealSnap = await getDoc(dealRef);
    if (dealSnap.exists()) {
      return { id: dealSnap.id, ...dealSnap.data() };
    } else {
      // console.log("No such deal!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching deal:", error);
  }
};

export const getDealByCategory = async (categoryId) => {
  try {
    const dealRef = doc(dealCollection, categoryId);
    const dealSnap = await getDoc(dealRef);
    if (dealSnap.exists()) {
      return { id: dealSnap.id, ...dealSnap.data() };
    } else {
      // console.log("No such deal!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching deal:", error);
  }
};

// Add a new deal
export const addDeal = async (
  dealName,
  merchantName,
  category,
  location,
  numRequired,
  postedBy,
  validUntil
) => {
  try {
    const dealRef = await addDoc(dealCollection, {
      dealName,
      merchantName,
      category,
      location,
      numRequired,
      postedBy,
      createdDateTime: new Date(),
      validUntil,
    });
    // console.log(`Deal ${dealRef.dealName} added successfully!`);
    return dealRef;
  } catch (error) {
    console.error("Error adding deal: ", error);
  }
};

// Update deal details
export const updateDeal = async (
  dealID,
  dealName,
  merchantName,
  category,
  location,
  numRequired,
  postedBy,
  validUntil
) => {
  try {
    const dealRef = doc(dealCollection, dealID);
    await updateDoc(dealRef, {
      dealName,
      merchantName,
      category,
      location,
      numRequired,
      postedBy,
      validUntil,
    });
    // console.log(`Deal ${dealID} updated successfully!`);
  } catch (error) {
    console.error("Error updating deal in Firestore:", error);
    throw error;
  }
};

// Delete a deal
export const deleteDeal = async (dealID) => {
  try {
    const dealRef = doc(dealCollection, dealID);
    await deleteDoc(dealRef);
    // console.log(`Deal ${dealID} deleted successfully!`);
  } catch (error) {
    console.error("Error deleting deal from Firestore:", error);
    throw error;
  }
};

// -------------------- Group Subcollection --------------------

/*
Fields:
- groupID: string
- isFull: boolean
- isClosed: boolean
- proposedDateTime: timestamp
- createdDateTime: timestamp
- chatRef: reference
- GroupMember: subcollection
*/

// Fetch all groups from a deal
export const getGroups = async (dealId) => {
  try {
    const groupsRef = collection(db, "Deal", dealId, "Group");
    const snapshot = await getDocs(groupsRef);
    return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error("Error fetching groups:", error);
    return [];
  }
};
// Fetch a single group by ID from a deal
export const getGroupById = async (dealId, groupId) => {
  try {
    const groupRef = doc(db, "Deal", dealId, "Group", groupId);
    const groupSnap = await getDoc(groupRef);
    if (groupSnap.exists()) {
      return { id: groupSnap.id, ...groupSnap.data() };
    } else {
      // console.log("No such group!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching group:", error);
  }
};

//Fetch a
export const getGroupByChatId = async (chatId) => {
  try {
    const chatRef = doc(chatCollection, chatId);
    const chatSnap = await getDoc(chatRef);

    if (!chatSnap.exists()) {
      // console.log("No such chat!");
      return null;
    }

    const chatData = chatSnap.data();
    if (!chatData.groupRef) {
      // console.log("No group reference found in chat!");
      return null;
    }

    const groupRefFromChat = chatData.groupRef;
    if (!groupRefFromChat.path) {
      // console.log("Invalid group reference path!");
      return null;
    }

    // Get the group members
    const groupData = groupRefFromChat.path.split("/");
    if (groupData.length < 4) {
      // console.log("Invalid group reference path format!");
      return null;
    }

    const dealId = groupData[1];
    const groupId = groupData[3];

    // Group is a document, not a collection
    const groupDocRef = doc(db, "Deal", dealId, "Group", groupId);
    const groupSnap = await getDoc(groupDocRef);

    if (!groupSnap.exists()) {
      // console.log("No such group!");
      return null;
    }

    const data = groupSnap.data();
    // Convert timestamp to formatted date string
    if (data.proposedDateTime) {
      const date = data.proposedDateTime.toDate();
      data.proposedDateTime = date.toLocaleString("en-SG", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      });
    }
    return { id: groupSnap.id, ...data };
  } catch (error) {
    console.error("Error fetching group by chat ID:", error);
    return null;
  }
};

// Add a new group
export const addGroup = async (dealId, isFull, proposedDateTime) => {
  try {
    // console.log("Adding group to deal:", {
    //   dealId,
    //   isFull,
    //   isClosed: false,
    //   proposedDateTime,
    //   chatRef: null,
    // });

    const groupsCollection = collection(db, "Deal", dealId, "Group");
    const groupRef = await addDoc(groupsCollection, {
      isFull,
      isClosed: false,
      proposedDateTime,
      createdDateTime: new Date(),
      chatRef: null,
    });

    // console.log(`Group added successfully with ID: ${groupRef.id}`);
    return groupRef;
  } catch (error) {
    console.error("Error adding group to Firestore:", error);
    throw error;
  }
};

// Update group details (not including chatRef)
export const updateGroup = async (
  dealId,
  groupId,
  isFull,
  isClosed,
  proposedDateTime,
  createdDateTime
) => {
  try {
    const groupRef = doc(db, "Deal", dealId, "Group", groupId);
    await updateDoc(groupRef, {
      isFull,
      isClosed,
      proposedDateTime,
      createdDateTime,
    });
    // console.log(`Group ${groupId} updated successfully!`);
  } catch (error) {
    console.error("Error updating group in Firestore:", error);
    throw error;
  }
};

// Delete a group
export const deleteGroup = async (dealId, groupId) => {
  try {
    const groupRef = doc(db, "Deal", dealId, "Group", groupId);
    await deleteDoc(groupRef);
    // console.log(`Group ${groupId} deleted successfully!`);
  } catch (error) {
    console.error("Error deleting group from Firestore:", error);
    throw error;
  }
};

// Close a group
export const closeGroup = async (dealId, groupId) => {
  try {
    const groupRef = doc(db, "Deal", dealId, "Group", groupId);
    await updateDoc(groupRef, { isClosed: true });
    // console.log(`Group ${groupId} closed successfully!`);
  } catch (error) {
    console.error("Error closing group in Firestore:", error);
    throw error;
  }
};

// -------------------- GroupMember Subcollection --------------------

/*
Fields:
- memberID: string
- user: reference
- joinDateTime: timestamp
- isLeader: boolean
*/

// Fetch all group members from a group
export const getGroupMembers = async (dealId, groupId) => {
  const groupMemberCollectionRef = collection(
    db,
    "Deal",
    dealId,
    "Group",
    groupId,
    "GroupMember"
  );
  const snapshot = await getDocs(groupMemberCollectionRef);
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
};

// Fetch a single group member by ID from a group
export const getGroupMemberIdByUserId = async (dealId, groupId, userId) => {
  const members = await getGroupMembers(dealId, groupId);
  const match = members.find((m) => m.user.id === userId);
  return match?.id || null;
};

// Fetch a single group member by ID from a group
export const getGroupMemberById = async (dealId, groupId, memberId) => {
  try {
    const groupMemberRef = doc(
      db,
      "Deal",
      dealId,
      "Group",
      groupId,
      "GroupMember",
      memberId
    );
    const groupMemberSnap = await getDoc(groupMemberRef);
    if (groupMemberSnap.exists()) {
      return { id: groupMemberSnap.id, ...groupMemberSnap.data() };
    } else {
      // console.log("No such group member!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching group member:", error);
  }
};

// Add a new group member
export const addGroupMember = async (dealId, groupId, user, isLeader) => {
  try {
    const groupMemberCollection = collection(
      db,
      "Deal",
      dealId,
      "Group",
      groupId,
      "GroupMember"
    );
    const groupMemberRef = await addDoc(groupMemberCollection, {
      user,
      isLeader,
      joinDateTime: new Date(),
    });
    // update isFull for group if necessary
    const dealRef = doc(dealCollection, dealId);
    const dealSnap = await getDoc(dealRef);
    const { numRequired } = dealSnap.data();
    const groupMemberSnap = await getDocs(groupMemberCollection);
    if (groupMemberSnap.size >= numRequired) {
      const groupRef = doc(db, "Deal", dealId, "Group", groupId);
      await updateDoc(groupRef, { isFull: true });
      // console.log(`Group ${groupId} is now full`);
    }
    // console.log(`Group member added with ID: ${groupMemberRef.id}`);
    return groupMemberRef;
  } catch (error) {
    console.error("Error adding group member to Firestore:", error);
    throw error;
  }
};

// Update group member details
export const updateGroupMember = async (
  dealId,
  groupId,
  memberId,
  user,
  isLeader
) => {
  try {
    const groupMemberRef = doc(
      db,
      "Deal",
      dealId,
      "Group",
      groupId,
      "GroupMember",
      memberId
    );
    await updateDoc(groupMemberRef, { user, isLeader });
    // console.log(`Group member ${memberId} updated successfully!`);
  } catch (error) {
    console.error("Error updating group member in Firestore:", error);
    throw error;
  }
};

// Delete a group member
export const deleteGroupMember = async (dealId, groupId, memberId) => {
  try {
    const groupMemberRef = doc(
      db,
      "Deal",
      dealId,
      "Group",
      groupId,
      "GroupMember",
      memberId
    );
    // update isFull for group if necessary
    const groupRef = doc(db, "Deal", dealId, "Group", groupId);
    const groupSnap = await getDoc(groupRef);
    const { isFull } = groupSnap.data();
    await deleteDoc(groupMemberRef);
    if (isFull) {
      await updateDoc(groupRef, { isFull: false });
    }
    // console.log(`Group member ${memberId} deleted successfully!`);
  } catch (error) {
    console.error("Error deleting group member from Firestore:", error);
    throw error;
  }
};

// -------------------- Chat Collection --------------------

const chatCollection = collection(db, "Chat");

/*
Fields:
- chatID: string
- chatName: string
- groupRef: reference
- Message: subcollection
*/

// Fetch all chats
export const getChats = async () => {
  const snapshot = await getDocs(chatCollection);
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
};

// Fetch a single chat by ID
export const getChat = async (chatID) => {
  try {
    const chatRef = doc(chatCollection, chatID);
    const chatSnap = await getDoc(chatRef);
    if (chatSnap.exists()) {
      return { id: chatSnap.id, ...chatSnap.data() };
    } else {
      // console.log("No such chat!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching chat:", error);
  }
};

// Add a new chat
export const addChat = async (chatName, groupRef) => {
  try {
    // Create the chat
    const chatRef = await addDoc(chatCollection, {
      chatName,
      groupRef,
      createdDateTime: new Date(),
    });
    // console.log(`Chat ${chatName} added successfully!`);

    // Get the group members
    const groupData = groupRef.path.split("/");
    const dealId = groupData[1];
    const dealRef = doc(dealCollection, dealId);
    const groupId = groupData[3];
    const groupMembers = await getGroupMembers(dealId, groupId);

    // Update the group's chatRef field with the new chat reference
    await updateDoc(groupRef, { chatRef: chatRef });

    // Add chat reference to each group member's chats array
    // Add deal reference to each group member's deals array
    const addChatPromises = groupMembers.map((member) =>
      Promise.all([
        addChatToUser(member.user.id, chatRef),
        addDealToUser(member.user.id, dealRef),
      ])
    );

    await Promise.all(addChatPromises);
    // console.log(`Chat added to all group members' chats arrays`);

    return chatRef;
  } catch (error) {
    console.error("Error adding chat to Firestore:", error);
    throw error;
  }
};

// Update chat details
export const updateChat = async (chatID, chatName, groupRef) => {
  try {
    const chatRef = doc(chatCollection, chatID);
    await updateDoc(chatRef, { chatName, groupRef });
    // console.log(`Chat ${chatID} updated successfully!`);
  } catch (error) {
    console.error("Error updating chat in Firestore:", error);
    throw error;
  }
};

// Delete a chat
export const deleteChat = async (chatID) => {
  try {
    const chatRef = doc(chatCollection, chatID);
    const chatSnap = await getDoc(chatRef);

    if (chatSnap.exists()) {
      const chatData = chatSnap.data();
      const groupRef = chatData.groupRef;

      // Get the group members
      const groupData = groupRef.path.split("/");
      const dealId = groupData[1];
      const groupId = groupData[3];
      const groupMembers = await getGroupMembers(dealId, groupId);

      // Remove chat reference from each group member's chats array
      const removeChatPromises = groupMembers.map((member) =>
        removeChatFromUser(member.user.id, chatRef)
      );

      await Promise.all(removeChatPromises);
      // console.log(`Chat removed from all group members' chats arrays`);

      // Delete the chat document
      await deleteDoc(chatRef);
      // console.log(`Chat ${chatID} deleted successfully!`);
    }
  } catch (error) {
    console.error("Error deleting chat from Firestore:", error);
    throw error;
  }
};

// Helper function to get all users in a chat
export const getChatUsers = async (chatId) => {
  try {
    const chatRef = doc(chatCollection, chatId);
    const chatSnap = await getDoc(chatRef);

    if (chatSnap.exists()) {
      const chatData = chatSnap.data();
      const groupRef = chatData.groupRef;

      // Get the group members
      const groupData = groupRef.path.split("/");
      const dealId = groupData[1];
      const groupId = groupData[3];
      const groupMembers = await getGroupMembers(dealId, groupId);

      // Get user details for each member
      const userPromises = groupMembers.map((member) =>
        getUser(member.user.id)
      );

      const users = await Promise.all(userPromises);
      return users.filter((user) => user !== null);
    }
    return [];
  } catch (error) {
    console.error("Error getting chat users:", error);
    return [];
  }
};

export const getGroupLeaderProfilePic = async (chatId) => {
  try {
    const chatRef = doc(chatCollection, chatId);
    const chatSnap = await getDoc(chatRef);

    if (chatSnap.exists()) {
      const chatData = chatSnap.data();
      const groupRef = chatData.groupRef;

      // Get the group members
      const groupData = groupRef.path.split("/");
      const dealId = groupData[1];
      const groupId = groupData[3];

      const groupMemberCollectionRef = collection(
        db,
        "Deal",
        dealId,
        "Group",
        groupId,
        "GroupMember"
      );
      const q = query(groupMemberCollectionRef, where("isLeader", "==", true));
      const leaderSnap = await getDocs(q);

      if (leaderSnap.empty) {
        // console.log("No group leader found!");
        return null;
      }

      const leaderDoc = leaderSnap.docs[0].data();
      const leaderRef = leaderDoc.user;

      // Get the leader userId
      const leaderRefArr = leaderRef.path.split("/");
      const leaderUserId = leaderRefArr[1];
      // console.log("leaderUserId: ", leaderUserId);

      // Get the leader user details
      try {
        const leaderUser = await getUser(leaderUserId);
        const leaderUserProfilePic = leaderUser.profilePicURL;
        if (!leaderUserProfilePic) {
          console.error("Could not find user details for leader");
          return null;
        }
        return leaderUserProfilePic;
      } catch (userError) {
        console.error("Error fetching leader user details:", userError);
        return null;
      }
    }
    // console.log("Chat document not found");
    return null;
  } catch (error) {
    console.error("Error fetching group leader:", error);
    return null;
  }
};

export const getGroupLeader = async (chatId) => {
  try {
    const chatRef = doc(chatCollection, chatId);
    const chatSnap = await getDoc(chatRef);

    if (chatSnap.exists()) {
      const chatData = chatSnap.data();
      const groupRef = chatData.groupRef;

      // Get the group members
      const groupData = groupRef.path.split("/");
      const dealId = groupData[1];
      const groupId = groupData[3];

      const groupMemberCollectionRef = collection(
        db,
        "Deal",
        dealId,
        "Group",
        groupId,
        "GroupMember"
      );
      const q = query(groupMemberCollectionRef, where("isLeader", "==", true));
      const leaderSnap = await getDocs(q);

      if (leaderSnap.empty) {
        // console.log("No group leader found!");
        return null;
      }

      const leaderDoc = leaderSnap.docs[0].data();
      const leaderRef = leaderDoc.user;

      // Get the leader userId
      const leaderRefArr = leaderRef.path.split("/");
      const leaderUserId = leaderRefArr[1];
      // console.log("leaderUserId: ", leaderUserId);

      // Get the leader user details
      try {
        const leaderUser = await getUser(leaderUserId);
        if (!leaderUser) {
          console.error("Could not find user details for leader");
          return null;
        }
        return leaderUser;
      } catch (userError) {
        console.error("Error fetching leader user details:", userError);
        return null;
      }
    }
    // console.log("Chat document not found");
    return null;
  } catch (error) {
    console.error("Error fetching group leader:", error);
    return null;
  }
};
// Add a user to a chat
export const addUserToChat = async (userId, chatId) => {
  try {
    const chatRef = doc(chatCollection, chatId);
    await updateDoc(chatRef, {
      GroupMember: arrayUnion({ user: userId, isLeader: false }),
    });
    // console.log(`User ${userId} added to chat ${chatId} successfully!`);
  } catch (error) {
    console.error("Error adding user to chat:", error);
    throw error;
  }
};

export const extractDealAndGroupIdFromChatId = async (chatId) => {
  try {
    const chatRef = doc(db, "Chat", chatId);
    const chatSnap = await getDoc(chatRef);

    if (!chatSnap.exists()) throw new Error("Chat document not found");

    const groupRef = chatSnap.data().groupRef;
    if (!groupRef?.path) throw new Error("groupRef missing in chat");

    const parts = groupRef.path.split("/"); // ["Deal", dealId, "Group", groupId]
    return { dealId: parts[1], groupId: parts[3] };
  } catch (err) {
    console.error("Failed to extract dealId/groupId:", err);
    return {};
  }
};

// -------------------- Message Subcollection --------------------

/*
Fields:
- messageID: string
- senderRef: reference
- timestamp: timestamp
- content: string
*/

// Fetch all messages from a chat
export const getMessages = async (chatId) => {
  try {
    const messagesCollection = collection(db, "Chat", chatId, "Message");
    const q = query(messagesCollection, orderBy("time", "asc")); // Order by time in asc order
    const snapshot = await getDocs(q);
    return snapshot.docs.map((doc) => {
      const data = doc.data();
      const senderId = data.senderRef
        ? data.senderRef.path.split("/")[1]
        : null;
      const time = data.time ? data.time.toDate() : null; // Convert Firebase timestamp to JavaScript Date
      return {
        id: doc.id,
        ...data,
        senderId,
        time, // Override time field with the converted date
      };
    });
  } catch (error) {
    console.error("Error fetching messages:", error);
    return [];
  }
};

export const getLatestMessage = async (chatId) => {
  try {
    const messagesCollection = collection(db, "Chat", chatId, "Message");
    const q = query(messagesCollection, orderBy("time", "desc"), limit(1));
    const snapshot = await getDocs(q);

    if (snapshot.empty) {
      return null;
    }

    return snapshot.docs[0].data().content;
  } catch (error) {
    console.error("Error fetching latest message:", error);
    return null;
  }
};

// Fetch a single message by ID from a chat
export const getMessageById = async (chatId, messageId) => {
  try {
    const messageRef = doc(db, "Chat", chatId, "Message", messageId);
    const messageSnap = await getDoc(messageRef);
    if (messageSnap.exists()) {
      return { id: messageSnap.id, ...messageSnap.data() };
    } else {
      // console.log("No such message!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching message:", error);
  }
};

// Add a new message
export const addMessage = async (chatId, senderId, content) => {
  try {
    const messagesCollection = collection(db, "Chat", chatId, "Message");
    const senderRef = doc(db, "User", senderId); // Create a proper document reference
    const messageRef = await addDoc(messagesCollection, {
      senderRef,
      content,
      time: new Date(),
    });
    // console.log(`Message added successfully with ID: ${messageRef.id}`);
    return messageRef;
  } catch (error) {
    console.error("Error adding message to Firestore:", error);
    throw error;
  }
};

// Update message details
export const updateMessage = async (chatId, messageId, senderRef, content) => {
  try {
    const messageRef = doc(db, "Chat", chatId, "Message", messageId);
    await updateDoc(messageRef, { senderRef, content });
    // console.log(`Message ${messageId} updated successfully!`);
  } catch (error) {
    console.error("Error updating message in Firestore:", error);
    throw error;
  }
};

// Delete a message
export const deleteMessage = async (chatId, messageId) => {
  try {
    const messageRef = doc(db, "Chat", chatId, "Message", messageId);
    await deleteDoc(messageRef);
    // console.log(`Message ${messageId} deleted successfully!`);
  } catch (error) {
    console.error("Error deleting message from Firestore:", error);
    throw error;
  }
};

// -------------------- Category Collection --------------------
/*
  To remove?
*/

const categoryCollection = collection(db, "Category");

/*
Fields:

*/

// Fetch all categories
export const getAllCategories = async () => {
  const categories = await getDocs(categoryCollection);
  return categories.docs.map((doc) => ({ ...doc.data() }));
};

export const getCategoryById = async (categoryID) => {
  try {
    const categoryRef = doc(categoryCollection, categoryID);
    const categorySnap = await getDoc(categoryRef);
    if (categorySnap.exists()) {
      return { id: categorySnap.id, ...categorySnap.data() };
    } else {
      // console.log("No such category!");
      return null;
    }
  } catch (error) {
    console.error("Error fetching category:", error);
  }
};

// Set up real-time listener for messages
export const onMessagesUpdate = (chatId, callback) => {
  const messagesCollection = collection(db, "Chat", chatId, "Message");
  const q = query(messagesCollection, orderBy("time", "asc"));

  return onSnapshot(
    q,
    (snapshot) => {
      const messages = snapshot.docs.map((doc) => {
        const data = doc.data();
        const senderId = data.senderRef
          ? data.senderRef.path.split("/")[1]
          : null;
        const time = data.time ? data.time.toDate() : null;
        return {
          id: doc.id,
          ...data,
          senderId,
          time,
        };
      });
      callback(messages);
    },
    (error) => {
      console.error("Error in message listener:", error);
      callback([], error);
    }
  );
};

// -------------------- Other Helper Functions --------------------

// Add a user to a group (handles chat and user)
export const addUserToGroup = async (dealId, groupId, userId) => {
  try {
    // Validate parameters
    if (!dealId || !groupId || !userId) {
      console.error("Parameter validation failed:", {
        dealId: dealId ? "present" : "missing",
        groupId: groupId ? "present" : "missing",
        userId: userId ? "present" : "missing",
      });
      throw new Error(
        "Missing required parameters: dealId, groupId, or userId is empty"
      );
    }

    // Handle userId which could be either a string ID or a user object
    let userRef;
    if (typeof userId === "string") {
      userRef = doc(userCollection, userId);
    } else if (userId && userId.id) {
      // If userId is an object with an id property
      userRef = doc(userCollection, userId.id);
    } else {
      console.error("Invalid userId format:", userId);
      throw new Error("Invalid userId format");
    }

    // Check if user is already in the group
    const groupMembers = await getGroupMembers(dealId, groupId);
    const userExists = groupMembers.some(
      (member) => member.user.path === userRef.path
    );
    if (userExists) {
      alert("You are already in this group!");
      return;
    }

    // Add user to group members
    await addGroupMember(dealId, groupId, userRef, false);

    // Find group chat
    const groupRef = doc(db, "Deal", dealId, "Group", groupId);
    const groupSnap = await getDoc(groupRef);

    if (!groupSnap.exists()) {
      throw new Error(`Group ${groupId} does not exist`);
    }

    const groupData = groupSnap.data();

    // Check if chat reference exists
    if (!groupData.chatRef) {
      console.warn(`No chat reference found for group ${groupId}`);
      // Still add deal reference to user
      const dealRef = doc(dealCollection, dealId);
      await addDealToUser(userRef.id, dealRef);
      return;
    }

    const chatRef = groupData.chatRef;

    // Add user to group chat
    await addUserToChat(userRef.id, chatRef.id);
    await addChatToUser(userRef.id, chatRef);

    // Add deal reference to user's deals array
    const dealRef = doc(dealCollection, dealId);
    await addDealToUser(userRef.id, dealRef);

    // console.log(`User ${userRef.id} successfully added to group ${groupId}`);
  } catch (error) {
    console.error("Error adding user to group:", error);
    throw error;
  }
};
