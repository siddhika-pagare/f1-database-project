// Import Firebase SDK from CDN
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-auth.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.3.1/firebase-analytics.js";

// Firebase Configuration
const firebaseConfig = {
    "apiKey": "AIzaSyA7MvYPBkzqAd8WwoIoVcYRhjrAhaQvtMU",
    "authDomain": "f1-database-ee8f6.firebaseapp.com",
    "projectId": "f1-database-ee8f6",
    "storageBucket": "f1-database-ee8f6.firebasestorage.app",
    "messagingSenderId": "77384837820",
    "appId": "1:77384837820:web:e957df4cf57af3d5b6beb9",
    "measurementId": "G-1292HYJH1Q"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

// Firestore API Base URL
const PROJECT_ID = "f1-database-ee8f6";
const API_KEY = "AIzaSyA7MvYPBkzqAd8WwoIoVcYRhjrAhaQvtMU";
const FIRESTORE_URL = `https://firestore.googleapis.com/v1/projects/${PROJECT_ID}/databases/(default)/documents/users?key=${API_KEY}`;

window.addEventListener("load", function() {
    updateUI(document.cookie);

    const signUpButton = document.getElementById("sign-up");
    if (signUpButton) {
        signUpButton.addEventListener('click', function(event) {
            event.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            createUserWithEmailAndPassword(auth, email, password)
                .then((userCredential) => {
                    const user = userCredential.user;
                    const userId = user.uid;
                    saveUserToFirestore(userId, email);
                    user.getIdToken().then((token) => {
                        document.cookie = "token=" + token + ";path=/;SameSite=Strict";
                        window.location = "/";
                    });
                })
                .catch((error) => {
                    console.error("Signup error: " + error.code + " " + error.message);
                    alert("Registration failed: " + error.message);
                });
        });
    }

    const loginButton = document.getElementById("login");
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            signInWithEmailAndPassword(auth, email, password)
                .then((userCredential) => {
                    const user = userCredential.user;
                    fetchUserFromFirestore(user.uid);
                    user.getIdToken().then((token) => {
                        document.cookie = "token=" + token + ";path=/;SameSite=Strict";
                        window.location = "/";
                    });
                })
                .catch((error) => {
                    console.error("Login error: " + error.code + " " + error.message);
                    alert("Login failed: " + error.message);
                });
        });
    }

    // Handle all sign-out buttons on the page
    document.querySelectorAll("#sign-out").forEach(signOutButton => {
        signOutButton.addEventListener('click', function() {
            signOut(auth)
                .then(() => {
                    document.cookie = "token=;path=/;SameSite=Strict";
                    window.location = "/";
                })
                .catch((error) => {
                    console.error("Sign-out error: " + error.message);
                    alert("Sign-out failed: " + error.message);
                });
        });
    });
});

function saveUserToFirestore(userId, email) {
    const userData = {
        "fields": {
            "userId": { "stringValue": userId },
            "email": { "stringValue": email },
            "createdAt": { "timestampValue": new Date().toISOString() }
        }
    };

    fetch(FIRESTORE_URL, {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Firestore save failed: ${response.status} - ${text}`);
            });
        }
        return response.json();
    })
    .then(data => console.log("User saved to Firestore:", data))
    .catch(error => {
        console.error("Error saving user:", error.message);
        alert("Failed to save user: " + error.message);
    });
}

function fetchUserFromFirestore(userId) {
    const url = `https://firestore.googleapis.com/v1/projects/${PROJECT_ID}/databases/(default)/documents/users/${userId}?key=${API_KEY}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Firestore fetch failed: ${response.status} - ${text}`);
                });
            }
            return response.json();
        })
        .then(data => console.log("User fetched from Firestore:", data))
        .catch(error => {
            console.error("Error fetching user:", error.message);
            alert("Failed to fetch user: " + error.message);
        });
}

function updateUI(cookie) {
    const token = parseCookieToken(cookie);
    const loginBoxes = document.querySelectorAll("#login-box");
    const signOutButtons = document.querySelectorAll("#sign-out");

    if (token.length > 0) {
        loginBoxes.forEach(box => box.hidden = true);
        signOutButtons.forEach(button => button.style.display = "inline-block");
    } else {
        loginBoxes.forEach(box => box.hidden = false);
        signOutButtons.forEach(button => button.style.display = "none");
    }
}

function parseCookieToken(cookie) {
    const strings = cookie.split(';');
    for (let i = 0; i < strings.length; i++) {
        const temp = strings[i].trim().split('=');
        if (temp[0] === "token") return temp[1];
    }
    return "";
}