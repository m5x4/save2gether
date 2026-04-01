<template>
  <Header></Header>
  <div id="page">
    <h1 id="header">Create New Deal</h1>

    <div id="formMapWrapper">
      <!-- Left: Form -->
      <form id="createDealForm">
        <div id="formContent">
          <fieldset>
            <legend>Deal Details</legend>

            <label for="dealName">Deal Name: </label>
            <p id="exampleText">
              Example: 1 for 1 at Starbucks, Buy 2 get 1 free at CottonOn
            </p>
            <input
              v-model="dealName"
              type="text"
              id="dealName"
              placeholder="Enter deal name"
              required
            />

            <label for="location">Location: </label>
            <input
              v-model.lazy="location"
              type="text"
              id="location"
              placeholder="Enter your location"
              required
            />

            <label for="merchantName">Merchant Name: </label>
            <input
              v-model.lazy="merchantName"
              type="text"
              id="merchantName"
              placeholder="Enter merchant's name"
              required
            />

            <label for="category">Category: </label>
            <select v-model="category" name="category" id="category" required>
              <option value="" disabled selected>Select Category</option>
              <option value="Food & Beverage">Food & Beverage</option>
              <option value="Lifestyle & Fitness">Lifestyle & Fitness</option>
              <option value="Travel & Attractions">Travel & Attractions</option>
              <option value="Retail">Retail</option>
              <option value="Games & Entertainment">
                Games & Entertainment
              </option>
            </select>

            <label for="expiryTime">Deal Expiry Time: </label>
            <input v-model="expiryTime" type="date" id="expiryTime" required />

            <label for="groupSize">Group Size: </label>
            <input
              v-model="groupSize"
              type="number"
              id="groupSize"
              placeholder="Enter group size"
              required
            />
          </fieldset>

          <fieldset>
            <legend>Group Details <span>(Optional)</span></legend>

            <label for="proposedDate">Proposed Date: </label>
            <input v-model="proposedDate" type="date" id="proposedDate" />

            <label for="proposedTime">Proposed Time: </label>
            <input v-model="proposedTime" type="time" id="proposedTime" />
          </fieldset>
        </div>

        <div id="submitButton">
          <button type="button" id="submit" @click="savetofs">Post Deal</button>
        </div>
      </form>

      <!-- Right: Map -->
      <div id="mapCard">
        <div id="mapTitle">Location Preview</div>
        <div id="map" class="map-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import Header from "../components/Header.vue";
import {
  addDeal,
  addGroup,
  addGroupMember,
  addChat,
} from "../firebase/firestore.js";
import { db, auth } from "../firebase/firebase.js";
import { useRouter } from "vue-router";
import { doc, collection, addDoc } from "firebase/firestore";

const location = ref("");
const merchantName = ref("");
const dealName = ref("");
const category = ref("");
const expiryTime = ref("");
const groupSize = ref("");
const proposedDate = ref("");
const proposedTime = ref("");

// -------------------- Save to Firestore --------------------

const router = useRouter();
const errorMessage = ref("");

const savetofs = async () => {
  try {
    // Form validation
    if (
      !location.value ||
      !dealName.value ||
      category.value === "default" ||
      !expiryTime.value ||
      !groupSize.value
    ) {
      errorMessage.value = "Please fill in all required fields";
      return;
    }

    // Get current user
    const user = auth.currentUser;
    // let user = auth.currentUser; // use this if you want to test, cos const cannot be edited
    if (!user) {
      // user = user || { uid: "ECsb4xLhc0WeVIgKfWLb2S6Wrh42" }; // For testing purposes using Max's uid
      errorMessage.value = "You must be logged in to create a deal";
      return;
    }

    // Create user reference
    const userRef = doc(db, "User", user.uid);

    // Format date as timestamp
    const validUntil = new Date(expiryTime.value);

    // Add the deal to Firestore
    const dealRef = await addDeal(
      dealName.value,
      merchantName.value,
      category.value,
      location.value,
      parseInt(groupSize.value),
      userRef,
      validUntil
    );

    // Only initialize group if both proposed date and time are provided
    if (proposedDate.value && proposedTime.value) {
      await initializeGroup(dealRef, userRef);
    }

    // console.log(`Deal created successfully with ID: ${dealRef.id}`);

    // Navigate to the deal detail page or deals list
    // router.push("/deals");
    router.push({
      name: "ViewDeal",
      query: { category: category.value },
    });
  } catch (error) {
    console.error("Error creating deal:", error);
    errorMessage.value = "Error creating deal. Please try again.";
  }
};

// New method to handle group initialization
const initializeGroup = async (dealRef, userRef) => {
  try {
    // Add group to Firestore with proposed date/time
    const proposedDateTime = new Date(
      `${proposedDate.value}T${proposedTime.value}`
    );
    const groupRef = await addGroup(
      dealRef.id,
      false, // isFull
      proposedDateTime
    );

    // Add the current user as the group leader
    await addGroupMember(dealRef.id, groupRef.id, userRef, true);

    // Create a chat for the group
    await addChat(`${dealName.value} Deal Chat`, groupRef); // change name of chat if needed

    // console.log(`Group initialized successfully with ID: ${groupRef.id}`);
  } catch (error) {
    console.error("Error initializing group:", error);
    throw error;
  }
};

// -------------------- Google Maps API Stuff --------------------

const map = ref(null);
const marker = ref(null);
const infoWindow = ref(null);
const API_KEY = import.meta.env.VITE_GOOGLEMAPS_API_KEY;

const loadGoogleMapsAPI = async () => {
  return new Promise((resolve, reject) => {
    if (window.google && window.google.maps) {
      resolve(); // If API is already loaded, resolve the promise
      return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&libraries=places`; // Replace with your actual API key
    script.async = true;
    script.defer = true;

    script.onload = () => {
      resolve(); // Resolve when the script is successfully loaded
    };
    script.onerror = (error) => {
      reject("Error loading Google Maps API: " + error);
    };

    document.head.appendChild(script); // Append the script tag to the document
  });
};

const initMap = async () => {
  try {
    // Load the Google Maps API
    await loadGoogleMapsAPI();

    // Initialize the map
    let center = { lat: 1.3521, lng: 103.8198 };
    map.value = new google.maps.Map(document.getElementById("map"), {
      center: center,
      zoom: 13,
      mapId: "4504f8b37365c3d0",
      mapTypeControl: false,
    });

    // Initialize Autocomplete
    const input = document.getElementById("location");
    const autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo("bounds", map.value);

    // Initialize marker and info window
    marker.value = new google.maps.Marker({
      map: map.value,
    });
    infoWindow.value = new google.maps.InfoWindow();

    // Handle place selection
    autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();

      if (!place.geometry || !place.geometry.location) {
        console.error("Place has no geometry.");
        return;
      }

      // console.log("Place selected:", place);
      location.value = place.formatted_address;
      merchantName.value = place.name; // do we need this? users will enter deal name in the form (also check line 260)

      // Center the map on the selected place
      if (place.geometry.viewport) {
        map.value.fitBounds(place.geometry.viewport);
      } else {
        map.value.setCenter(place.geometry.location);
        map.value.setZoom(17);
      }

      // Update marker position
      marker.value.setPosition(place.geometry.location);

      // Update info window

      updateInfoWindow(
        `<div>
          <strong>${place.name}</strong><br>
          ${place.formatted_address}<br>
          ${place.rating} / 5 stars <br>
          ${place.current_opening_hours.open_now ? "Open now" : "Closed"} <br>
        </div>`,
        place.geometry.location
      );
    });
  } catch (error) {
    console.error("Error initializing the map:", error);
  }
};

// Function to update the info window
const updateInfoWindow = (content, position) => {
  infoWindow.value.setContent(content);
  infoWindow.value.setPosition(position);
  infoWindow.value.open(map.value, marker.value);
};

// Initialize the map when the component is mounted
onMounted(async () => {
  await initMap();
});
</script>

<style>
/* General Page */
#page {
  padding: 30px 50px;
  background-color: #f4f6f8;
  font-family: "Segoe UI", sans-serif;
  color: #17334b;
  height: calc(100vh - 90px); /* Full viewport height */
  display: flex;
  flex-direction: column;
  box-sizing: border-box; /* Include padding in the height */
  overflow: hidden;
}

/* Header */
#header {
  font-size: 36px;
  font-weight: 700;
  margin-top: 0px;
  margin-bottom: 30px;
}

/* Layout Wrapper */
#formMapWrapper {
  display: flex;
  gap: 40px;
  flex: 1; /* Take remaining space */
  min-height: 0; /* Important for children to respect parent height */
}

/* Form */
#createDealForm {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  padding: 20px;
  min-height: 0; /* Important for children to respect parent height */
}

#formContent {
  flex: 1;
  overflow-y: auto; /* Only scroll when needed */
  padding-right: 10px;
  min-height: 0; /* Important for scroll to work properly */
}

fieldset {
  border: none;
  padding: 0;
  margin-bottom: 20px;
}

legend {
  font-size: 20px;
  font-weight: 600;
  color: #234;
  border-left: 4px solid #17334b;
  padding-left: 10px;
  margin-bottom: 12px;
  margin-top: 15px;
}

legend span {
  font-weight: 400;
  font-size: 14px;
  color: #666;
}

label {
  font-size: 15px;
  font-weight: 600;
  margin-top: 8px;
  margin-bottom: 6px;
  display: block;
}

/* Example Text */
#exampleText {
  font-size: 14px;
  color: #999;
  margin-bottom: 10px;
  font-style: italic;
  margin-top: 5px;
}

input,
select {
  padding: 8px;
  font-size: 15px;
  border-radius: 10px;
  border: 1px solid #ccc;
  width: 100%;
  box-sizing: border-box;
  background-color: #fefefe;
  margin-bottom: 10px;
}

/* Submit Button */
#submitButton {
  margin-top: auto; /* Push to bottom */
  display: flex;
  justify-content: center;
  width: 100%;
  background-color: #fff;
  padding: 15px 0;
  border-top: 1px solid #eee;
}

#submit {
  background-color: #17334b;
  color: white;
  padding: 14px 36px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s ease;
  width: 100%;
}

#submit:hover {
  background-color: #265a7e;
}

/* Map Card */
#mapCard {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  min-height: 0; /* Important for children to respect parent height */
}

#mapTitle {
  padding: 15px 20px;
  font-size: 18px;
  font-weight: 600;
  background-color: #17334b;
  color: white;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
}

#map {
  flex: 1;
  width: 100%;
  min-height: 0; /* Allow map to shrink */
}

/* Responsive */
@media (max-width: 1400px) {
  #page {
    padding: 30px 40px;
  }

  #formMapWrapper {
    gap: 30px;
  }
}

@media (max-width: 1000px) {
  html,
  body {
    overflow: auto; /* Allow scrolling on mobile */
    height: auto;
  }

  #page {
    padding: 20px;
    height: auto; /* For mobile, let it scroll vertically */
    min-height: 100vh;
    overflow: visible;
  }

  #formMapWrapper {
    flex-direction: column;
    gap: 20px;
  }

  #mapCard {
    height: 400px; /* Fixed height on mobile */
    min-height: 400px;
  }

  #createDealForm {
    padding: 20px;
  }

  #header {
    font-size: 28px;
    margin-bottom: 20px;
  }
}

@media (max-width: 600px) {
  #page {
    padding: 20px;
  }

  #formMapWrapper {
    gap: 10px;
  }

  #createDealForm {
    padding: 15px;
  }

  #header {
    font-size: 24px;
    margin-bottom: 15px;
  }

  #mapCard {
    height: 300px;
  }
}

/* Add this to your HTML file if not already present */
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>
