const root = document.getElementById("root");

//displays the loading during API dashboard requests
function displayLoading() {
    root.innerHTML = `
    <div>
        <h1> 
            Loading dashboard...
        </h1>
    </div>
    `;
}

//displays errors sent from loadDashboard
function displayError(message) {
    root.innerHTML = `
    <div>
        <h1>
            ${message}
        </h1>
    </div>
    `;
}

//displays data, to be expanded in later increments
function displayDashboard (data) {
    root.innerHTML = `
    <div>
        <h1>Dashboard</h1>
        <pre>${JSON.stringify(data, null, 2)}</pre>
    </div>
    `;
}

async function loadDashboard() {
  displayLoading();

  try {
    const response = await fetch("/api/dashboard");

    if (!response.ok) {
      throw new Error("Failed to fetch dashboard data");
    }

    const data = await response.json();
    displayDashboard(data);

    } 
    catch (err) {
        displayError(err.message);
    }
}

//runs when the page loads
loadDashboard();