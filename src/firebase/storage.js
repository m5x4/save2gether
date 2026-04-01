import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { storage } from "./firebase.js";

// Function to generate a hash from a string
const generateHash = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
};

// Function to get file extension
const getFileExtension = (filename) => {
  return filename.slice(((filename.lastIndexOf(".") - 1) >>> 0) + 2);
};

// Upload a file and get its download URL
export const uploadFile = async (file, path) => {
  try {
    // Create a storage reference
    const storageRef = ref(storage, path);

    // Upload the file
    const snapshot = await uploadBytes(storageRef, file);

    // Get the download URL
    const downloadURL = await getDownloadURL(snapshot.ref);

    return downloadURL;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};

// Upload a profile picture
export const uploadProfilePicture = async (file, userId) => {
  try {
    // Check file size (100KB = 100 * 1024 bytes)
    if (file.size > 100 * 1024) {
      throw new Error("File size must be less than 100KB");
    }

    // Generate a unique filename using timestamp and hash
    const timestamp = Date.now();
    const originalName = file.name;
    const fileExtension = getFileExtension(originalName);
    const hashedName = generateHash(originalName + timestamp);
    const uniqueFileName = `${hashedName}.${fileExtension}`;

    // Create a unique path for the profile picture
    const path = `profile-pictures/${userId}/${uniqueFileName}`;

    // Upload the file and get the URL
    const downloadURL = await uploadFile(file, path);

    return downloadURL;
  } catch (error) {
    console.error("Error uploading profile picture:", error);
    throw error;
  }
};
