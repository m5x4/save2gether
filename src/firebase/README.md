# Save2Gether Firebase Data Model

This document outlines the database structure used in the Save2Gether application. Our data model is built using Firebase Firestore and follows a collection-document structure with references between related entities.

## Database Collections Overview

![Database Schema](/assets/save2gether_schema.jpg)

## User Collection

The `User` collection stores information about application users.

**Document fields:**

- `userID` (string): Unique identifier for the user
- `firstName` (string): User's first name
- `lastName` (string): User's last name
- `profilePicURL` (string): URL to the user's profile picture
- `joinDateTime` (timestamp): When the user joined the platform
- `chats` (array of chat references): References to chats the user is part of
- `deals` (array of deal references): References to deals the user is involved in

### Review Subcollection

Each user document contains a `Review` subcollection that stores reviews about the user.

**Document fields:**

- `reviewID` (string): Unique identifier for the review
- `reviewerRef` (reference): Reference to the user who wrote the review
- `content` (string): Text content of the review
- `rating` (number): Numerical rating (typically 1-5)

## Deal Collection

The `Deal` collection stores information about deals available on the platform.

**Document fields:**

- `dealID` (string): Unique identifier for the deal
- `merchantName` (string): Name of the merchant offering the deal
- `dealName` (string): Name of the deal
- `category` (string): Category the deal belongs to
- `clickCount` (number): Number of times the deal has been viewed
- `location` (string): Geographic location of the deal
- `numRequired` (number): Number of people required for the deal
- `postedBy` (reference): Reference to the user who posted the deal
- `createdDateTime` (timestamp): When the deal was created
- `validUntil` (timestamp): When the deal expires

### Group Subcollection

Each deal document contains a `Group` subcollection that stores information about groups formed for the deal.

**Document fields:**

- `groupID` (string): Unique identifier for the group
- `isFull` (boolean): Whether the group has reached its required number of members
- `isClosed` (boolean): Whether the group is closed for new members
- `proposedDateTime` (timestamp): Proposed date and time for meeting
- `createdDateTime` (timestamp): When the group was created
- `chatRef` (reference): Reference to the chat for this group

#### GroupMember Subcollection

Each group document contains a `GroupMember` subcollection that stores information about members of the group.

**Document fields:**

- `memberID` (string): Unique identifier for the group member
- `user` (reference): Reference to the user
- `joinDateTime` (timestamp): When the user joined the group
- `isLeader` (boolean): Whether the user is the group leader

## Chat Collection

The `Chat` collection stores information about chat groups.

**Document fields:**

- `chatID` (string): Unique identifier for the chat
- `chatName` (string): Name of the chat
- `groupRef` (reference): Reference to the group this chat belongs to

### Message Subcollection

Each chat document contains a `Message` subcollection that stores the chat messages.

**Document fields:**

- `messageID` (string): Unique identifier for the message
- `senderRef` (reference): Reference to the user who sent the message
- `timestamp` (timestamp): When the message was sent
- `content` (string): Content of the message

## Relationships Between Collections

1. **User to Review**: One-to-many relationship (one user can have many reviews)
2. **User to Deal**: Many-to-many relationship (users can be involved in multiple deals, deals can have multiple users)
3. **Deal to Group**: One-to-many relationship (one deal can have multiple groups)
4. **Group to GroupMember**: One-to-many relationship (one group can have multiple members)
5. **Group to Chat**: One-to-one relationship (each group has one chat)
6. **Chat to Message**: One-to-many relationship (one chat can have multiple messages)

## Reference Types

In the data model:

- Green references (`reference`) indicate references to User documents
- Purple references (`reference`) indicate references to Deal documents
- Blue references (`reference`) indicate references to Chat documents

## API Functions

This data model is supported by a comprehensive set of API functions in the `firestore.js` file, including:

### User Management

- `getUsers()`, `getUser(userID)`, `addUser()`, `updateUser()`, `deleteUser()`
- `addChatToUser()`, `removeChatFromUser()`, `getUserChats()`
- `addDealToUser()`, `removeDealFromUser()`, `getUserDeals()`

### Review Management

- `getReviews()`, `getReviewById()`, `addReview()`, `updateReview()`, `deleteReview()`

### Deal Management

- `getDeals()`, `getDeal()`, `getDealByCategory()`, `addDeal()`, `updateDeal()`, `deleteDeal()`

### Group Management

- `getGroups()`, `getGroupById()`, `getGroupByChatId()`, `addGroup()`, `updateGroup()`, `deleteGroup()`, `closeGroup()`

### Group Member Management

- `getGroupMembers()`, `getGroupMemberById()`, `addGroupMember()`, `updateGroupMember()`, `deleteGroupMember()`

### Chat Management

- `getChats()`, `getChat()`, `addChat()`, `updateChat()`, `deleteChat()`
- `getChatUsers()`, `getGroupLeader()`, `addUserToChat()`

### Message Management

- `getMessages()`, `getLatestMessage()`, `getMessageById()`, `addMessage()`, `updateMessage()`, `deleteMessage()`
- `onMessagesUpdate()` (real-time listener)

## Usage Notes

1. When adding a user to a group, use the `addUserToGroup()` helper function to ensure all necessary references are created.
2. Use Firebase references for connecting documents, not just IDs.
3. Use the real-time listener `onMessagesUpdate()` for implementing chat functionality.
4. Always check if a reference exists before trying to access it to avoid errors.
