document.addEventListener('DOMContentLoaded', function () {
  const apiEndpoint = 'https://video-backend-xyz-gyarggbebrezg2bk.ukwest-01.azurewebsites.net'; // Updated API URL

  let loggedInUser = null; // Store logged-in user data

  // Get elements for Login and Sign Up
  const loginModal = document.getElementById('login-modal');
  const signupModal = document.getElementById('signup-modal');
  const loginBtn = document.getElementById('login-btn');
  const signupBtn = document.getElementById('signup-btn');
  const uploadForm = document.getElementById('upload-form');  // Video upload form
  const usernameDisplay = document.getElementById('username-display'); // Display username

  // Open Login Modal
  loginBtn.addEventListener('click', () => {
    loginModal.style.display = 'flex'; // Show the modal
  });

  // Open Sign Up Modal
  signupBtn.addEventListener('click', () => {
    signupModal.style.display = 'flex'; // Show the modal
  });

  // Close Modals on Outside Click
  window.addEventListener('click', (event) => {
    if (event.target === loginModal) {
      loginModal.style.display = 'none';
    }
    if (event.target === signupModal) {
      signupModal.style.display = 'none';
    }
  });

  // Handle Login Form Submission
  document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch(`${apiEndpoint}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert('Login successful!');
          loggedInUser = { username, role: data.role };
          document.getElementById('login-modal').style.display = 'none';
          updateHeader();
        } else {
          alert(data.message || 'Invalid username or password.');
        }
      })
      .catch(error => console.error('Login Error:', error));
  });

  // Handle Sign Up Form Submission
  document.getElementById('signup-form').addEventListener('submit', function (event) {
    event.preventDefault();
    console.log("Form submitted");  // Check if the form is being submitted

    const username = document.getElementById('signup-username').value;
    const password = document.getElementById('signup-password').value;
    const role = document.getElementById('user-role').value;

    // Sending the signup request to the backend
    fetch(`${apiEndpoint}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role }),
    })
      .then(response => response.json())
      .then(data => {
        console.log(data);  // Check what data is returned
        if (data.success) {
          alert('Sign up successful! Please log in.');
          document.getElementById('signup-modal').style.display = 'none';
        } else {
          alert(data.message || 'Error during sign up.');
        }
      })
      .catch(error => {
        console.error('Signup Error:', error);
        alert('Failed to sign up.');
      });
  });

  // Update header with login status and show upload form for creators
  function updateHeader() {
    const loginBtn = document.getElementById('login-btn');
    const signupBtn = document.getElementById('signup-btn');
    const loggedInUserDiv = document.getElementById('logged-in-user');
    const uploadForm = document.getElementById('upload-form');
    const usernameDisplay = document.getElementById('username-display');
  
    if (loggedInUser) {
      console.log(`Logged in as: ${loggedInUser.username}, Role: ${loggedInUser.role}`);  // Add this log
  
      loginBtn.style.display = 'none';
      signupBtn.style.display = 'none';
      loggedInUserDiv.style.display = 'flex';
      usernameDisplay.textContent = `Welcome, ${loggedInUser.username}`;
  
      // Show the upload form if the user is a creator
      if (loggedInUser.role === 'creator') {
        console.log('Showing upload form'); // Add this log
        uploadForm.style.display = 'block'; // Show upload form
      }
    } else {
      loginBtn.style.display = 'inline-block';
      signupBtn.style.display = 'inline-block';
      loggedInUserDiv.style.display = 'none';
      usernameDisplay.textContent = '';
      uploadForm.style.display = 'none'; // Hide the upload form when not logged in
    }
  }
  

  // Handle Log Out
  document.getElementById('logout-btn').addEventListener('click', function () {
    loggedInUser = null; // Clear the logged-in user data
    alert('You have been logged out.');

    // Hide the upload form if the user is a creator
    document.getElementById('upload-form').style.display = 'none';

    // Update the header to reflect the logout state
    updateHeader();
  });

  // Fetch Videos on Page Load
  function fetchVideos() {
    fetch(`${apiEndpoint}/videos`)
      .then(response => response.json())
      .then(data => {
        const videoContainer = document.getElementById('video-container');
        videoContainer.innerHTML = ''; // Clear any existing content
        data.forEach(video => {
          const videoCard = document.createElement('div');
          videoCard.classList.add('video-card');
          videoCard.innerHTML = `
            <img src="${video.thumbnail}" alt="${video.title}">
            <div class="video-info">
              <h3>${video.title}</h3>
              <p>${video.description}</p>
            </div>
          `;
          videoContainer.appendChild(videoCard);
        });
      })
      .catch(error => console.error('Error fetching videos:', error));
  }

  // Initial page setup
  fetchVideos();
  updateHeader();
});
