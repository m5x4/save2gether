<template>
  <div class="dashboard-grid">
    <!-- Reviews Section -->
    <div class="dashboard-card">
      <h3>Individual Reviews</h3>
      <div class="chart-container">
        <canvas ref="scatterChartCanvas"></canvas>
      </div>
    </div>

    <!-- Average Rating Section -->
    <div class="dashboard-card">
      <h3>Average Rating Over Time</h3>
      <div class="chart-container">
        <canvas ref="lineChartCanvas"></canvas>
      </div>
    </div>

    <!-- Rating Distribution Section -->
    <div class="dashboard-card">
      <h3>Rating Distribution</h3>
      <div class="chart-container">
        <canvas ref="pieChartCanvas"></canvas>
      </div>
    </div>

    <!-- Deal Categories Section -->
    <div class="dashboard-card">
      <h3>Deal Categories Joined</h3>
      <div class="chart-container">
        <canvas ref="barChartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart } from "chart.js/auto";
import { getReviews, getUser, getDeal } from "../firebase/firestore";
// Import the date adapter for Chart.js
import "chartjs-adapter-date-fns";

const props = defineProps({
  userId: String,
});

const chartData = ref([]);
const averageData = ref([]);
const ratingDistribution = ref([]);
const dealCategories = ref([]);

const scatterChartCanvas = ref(null);
const lineChartCanvas = ref(null);
const pieChartCanvas = ref(null);
const barChartCanvas = ref(null);
let scatterChart = null;
let lineChart = null;
let pieChart = null;
let barChart = null;

// Function to fetch and process all the data needed for charts
const fetchData = async () => {
  if (props.userId) {
    try {
      await Promise.all([fetchReviews(), fetchDealCategories()]);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  } else {
    // Reset data if no userId is provided
    chartData.value = [];
    averageData.value = [];
    ratingDistribution.value = [];
    dealCategories.value = [];
  }
};

// Function to fetch and process reviews
const fetchReviews = async () => {
  try {
    // Use the getReviews method from firestore.js
    const reviews = await getReviews(props.userId);
    // console.log("Fetched Reviews:", reviews);

    // Transform the data for the scatter chart
    chartData.value = reviews.map((review) => ({
      x: new Date(review.createdDateTime.seconds * 1000),
      y: review.rating,
      content: review.content || "No content available",
    }));

    // Calculate average rating over time
    calculateAverageRatingOverTime(reviews);

    // Calculate rating distribution
    calculateRatingDistribution(reviews);

    // console.log("Chart Data:", chartData.value);
  } catch (error) {
    console.error("Error fetching reviews:", error);
    chartData.value = [];
    averageData.value = [];
    ratingDistribution.value = [];
  }
};

// Function to calculate average rating over time
const calculateAverageRatingOverTime = (reviews) => {
  // Sort reviews by date
  const sortedReviews = [...reviews].sort(
    (a, b) => a.createdDateTime.seconds - b.createdDateTime.seconds
  );

  // Calculate running average
  let totalRating = 0;
  let totalCount = 0;

  averageData.value = sortedReviews.map((review) => {
    const date = new Date(review.createdDateTime.seconds * 1000);
    totalRating += review.rating;
    totalCount += 1;

    return {
      x: date,
      y: totalRating / totalCount,
    };
  });
};

// Function to calculate rating distribution
const calculateRatingDistribution = (reviews) => {
  const distribution = Array(5).fill(0);
  reviews.forEach((review) => {
    distribution[review.rating - 1]++;
  });

  ratingDistribution.value = distribution.map((count, index) => ({
    rating: index + 1,
    count: count,
  }));
};

// Function to fetch and calculate deal categories
const fetchDealCategories = async () => {
  try {
    // Get user data to access deals array
    const userData = await getUser(props.userId);

    // Define all possible categories
    const allCategories = [
      "Food & Beverage",
      "Lifestyle & Fitness",
      "Travel & Attractions",
      "Retail",
      "Games & Entertainment",
    ];

    if (!userData || !userData.deals || userData.deals.length === 0) {
      // console.log("No deals found for user");
      // Initialize with all categories set to 0
      dealCategories.value = allCategories.map((category) => ({
        category,
        count: 0,
      }));
      return;
    }

    // Initialize categoryCount with all categories set to 0
    const categoryCount = {};
    allCategories.forEach((category) => {
      categoryCount[category] = 0;
    });

    // Process each deal reference
    const dealPromises = userData.deals.map(async (dealRef) => {
      const dealId = dealRef.id;
      const dealData = await getDeal(dealId);
      return dealData;
    });

    const dealResults = await Promise.all(dealPromises);

    // Count categories from the results
    dealResults.forEach((dealData) => {
      if (dealData && dealData.category) {
        categoryCount[dealData.category] =
          (categoryCount[dealData.category] || 0) + 1;
      }
    });

    // Transform data for the bar chart, ensuring all categories are included
    dealCategories.value = allCategories.map((category) => ({
      category,
      count: categoryCount[category] || 0,
    }));

    // console.log("Deal Categories:", dealCategories.value);
  } catch (error) {
    console.error("Error fetching deal categories:", error);
    // Initialize with all categories set to 0 in case of error
    dealCategories.value = [
      { category: "Food & Beverage", count: 0 },
      { category: "Lifestyle & Fitness", count: 0 },
      { category: "Travel & Attractions", count: 0 },
      { category: "Retail", count: 0 },
      { category: "Games & Entertainment", count: 0 },
    ];
  }
};

// Watch for userId changes to load new data
watch(
  () => props.userId,
  (newUserId) => {
    if (newUserId) {
      fetchData();
    } else {
      // Reset data if userId is cleared
      chartData.value = [];
      averageData.value = [];
      ratingDistribution.value = [];
      dealCategories.value = [];
    }
  }
);

// Run once when component is mounted
onMounted(() => {
  if (props.userId) {
    fetchData();
  }
});

// Watch for changes in chartData and update the scatter chart
watch(
  chartData,
  (newData) => {
    if (newData.length > 0 && scatterChartCanvas.value) {
      if (scatterChart) {
        scatterChart.destroy();
      }
      const ctx = scatterChartCanvas.value.getContext("2d");
      scatterChart = new Chart(ctx, {
        type: "scatter",
        data: {
          datasets: [
            {
              label: "Reviews",
              data: newData,
              backgroundColor: "rgba(30, 70, 112, 0.8)",
              borderColor: "rgba(30, 70, 112, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: "time",
              time: {
                unit: "month",
                displayFormats: {
                  month: "MMM yyyy",
                },
                tooltipFormat: "MMM d, yyyy",
              },
              title: {
                display: true,
                text: "Date",
              },
            },
            y: {
              beginAtZero: true,
              max: 5,
              title: {
                display: true,
                text: "Rating",
              },
            },
          },
        },
      });
    }
  },
  { deep: true }
);

// Watch for changes in averageData and update the line chart
watch(
  averageData,
  (newData) => {
    if (newData.length > 0 && lineChartCanvas.value) {
      if (lineChart) {
        lineChart.destroy();
      }
      const ctx = lineChartCanvas.value.getContext("2d");
      lineChart = new Chart(ctx, {
        type: "line",
        data: {
          datasets: [
            {
              label: "Average Rating",
              data: newData,
              borderColor: "rgba(255, 99, 132, 1)",
              backgroundColor: "rgba(255, 99, 132, 0.2)",
              borderWidth: 2,
              fill: true,
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          elements: {
            point: {
              radius: 0, // Hide individual points
              hoverRadius: 5, // Show points on hover
            },
            line: {
              tension: 0.4, // Curve smoothing
            },
          },
          scales: {
            x: {
              type: "time",
              time: {
                unit: "month",
                displayFormats: {
                  month: "MMM yyyy",
                },
                tooltipFormat: "MMM d, yyyy",
              },
              title: {
                display: true,
                text: "Date",
              },
            },
            y: {
              beginAtZero: true,
              max: 5,
              title: {
                display: true,
                text: "Average Rating",
              },
            },
          },
        },
      });
    }
  },
  { deep: true }
);

// Watch for changes in ratingDistribution and update the pie chart
watch(
  ratingDistribution,
  (newData) => {
    if (newData.length > 0 && pieChartCanvas.value) {
      if (pieChart) {
        pieChart.destroy();
      }
      const ctx = pieChartCanvas.value.getContext("2d");
      pieChart = new Chart(ctx, {
        type: "pie",
        data: {
          labels: newData.map(
            (item) => "★".repeat(item.rating) // + "☆".repeat(5 - item.rating)
          ),
          datasets: [
            {
              data: newData.map((item) => item.count),
              // backgroundColor: [
              //   "RGBA(56, 207, 119, 0.8)",
              //   "RGBA(47, 161, 159, 0.8)",
              //   "RGBA(28, 105, 173, 0.8)",
              //   "RGBA(138, 65, 85, 0.8)",
              //   "RGBA(217, 38, 11, 0.8)",
              // ],
              // borderColor: [
              //   "#38CF77",
              //   "#2FA19F",
              //   "#1C69AD",
              //   "#8A4155",
              //   "#D9260B",
              // ],
              backgroundColor: [
                "rgba(255, 99, 132, 1)",
                "rgba(255, 159, 64, 1)",
                "rgba(255, 205, 86, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(75, 192, 192, 1)",
              ],
              borderColor: [
                "rgba(255, 99, 132, 1)",
                "rgba(255, 159, 64, 1)",
                "rgba(255, 205, 86, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(75, 192, 192, 1)",
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          layout: {
            padding: {
              left: 110 /* Adjust this value to balance the right legend */,
              right: 0,
              top: 0,
              bottom: 0,
            },
          },
          plugins: {
            legend: {
              position: "right",
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || "";
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                },
              },
            },
          },
        },
      });
    }
  },
  { deep: true }
);

// Watch for changes in dealCategories and update the bar chart
watch(
  dealCategories,
  (newData) => {
    if (newData.length > 0 && barChartCanvas.value) {
      if (barChart) {
        barChart.destroy();
      }
      const ctx = barChartCanvas.value.getContext("2d");
      barChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: newData.map((item) => item.category),
          datasets: [
            {
              label: "Number of Deals",
              data: newData.map((item) => item.count),
              backgroundColor: [
                "rgba(255, 99, 132, 0.6)", // Food & Beverage - Pink
                "rgba(54, 162, 235, 0.6)", // Lifestyle & Fitness - Blue
                "rgba(255, 206, 86, 0.6)", // Travel & Attractions - Yellow
                "rgba(75, 192, 192, 0.6)", // Retail - Teal
                "rgba(153, 102, 255, 0.6)", // Games & Entertainment - Purple
              ],
              borderColor: [
                "rgba(255, 99, 132, 1)", // Food & Beverage - Pink
                "rgba(54, 162, 235, 1)", // Lifestyle & Fitness - Blue
                "rgba(255, 206, 86, 1)", // Travel & Attractions - Yellow
                "rgba(75, 192, 192, 1)", // Retail - Teal
                "rgba(153, 102, 255, 1)", // Games & Entertainment - Purple
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                precision: 0,
              },
              title: {
                display: true,
                text: "Number of Deals",
              },
            },
            x: {
              title: {
                display: true,
                text: "Category",
              },
            },
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `${context.raw} deals`;
                },
              },
            },
          },
        },
      });
    }
  },
  { deep: true }
);
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.dashboard-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.dashboard-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 1.2em;
  text-align: center;
  width: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
  position: relative;
  display: flex;
  justify-content: center;
}

.chart-container canvas {
  max-width: 100%;
  max-height: 100%;
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
