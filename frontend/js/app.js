// ======================================
// SADA-AI Dashboard
// app.js
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("SADA-AI Dashboard Loaded");

    initializeSidebar();

    initializeCards();

    initializeHeroButton();

    animateCards();

});


// ======================================
// Sidebar Active Menu
// ======================================

function initializeSidebar() {

    const menus = document.querySelectorAll(".menu li");

    menus.forEach(menu => {

        menu.addEventListener("click", () => {

            menus.forEach(item => {

                item.classList.remove("active");

            });

            menu.classList.add("active");

        });

    });

}


// ======================================
// Feature Card
// ======================================

function initializeCards() {

    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-8px)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0px)";

        });

    });

}


// ======================================
// Hero Button
// ======================================

function initializeHeroButton() {

    const heroButton = document.querySelector(".hero button");

    if (!heroButton) return;

    heroButton.addEventListener("click", () => {

        window.scrollTo({

            top: document.querySelector(".cards").offsetTop - 30,

            behavior: "smooth"

        });

    });

}


// ======================================
// Fade Animation
// ======================================

function animateCards() {

    const cards = document.querySelectorAll(".card");

    cards.forEach((card, index) => {

        card.style.opacity = 0;

        card.style.transform = "translateY(30px)";

        setTimeout(() => {

            card.style.transition = ".6s";

            card.style.opacity = 1;

            card.style.transform = "translateY(0px)";

        }, index * 150);

    });

}


// ======================================
// Toast Notification
// ======================================

function showToast(message) {

    const toast = document.createElement("div");

    toast.className = "toast";

    toast.innerHTML = message;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.classList.add("show");

    }, 100);

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => {

            toast.remove();

        }, 500);

    }, 2500);

}


// ======================================
// Open Feature
// ======================================

function openFeature(feature) {

    showToast("Membuka fitur : " + feature);

}


// ======================================
// Future API
// ======================================

// Nanti tinggal ganti URL FastAPI
const API_URL = "http://127.0.0.1:8000";


// ======================================
// Chatbot API
// ======================================

async function askAI(question) {

    try {

        const response = await fetch(API_URL + "/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: question

            })

        });

        const data = await response.json();

        return data.answer;

    }

    catch (error) {

        console.error(error);

        return "Server tidak dapat dihubungi.";

    }

}


// ======================================
// Report API
// ======================================

async function summarize(text) {

    try {

        const response = await fetch(API_URL + "/summary", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                text: text

            })

        });

        return await response.json();

    }

    catch (error) {

        console.log(error);

    }

}


// ======================================
// Prediction API
// ======================================

async function predict(dataset) {

    try {

        const response = await fetch(API_URL + "/predict", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                dataset: dataset

            })

        });

        return await response.json();

    }

    catch (error) {

        console.log(error);

    }

}


// ======================================
// Anomaly API
// ======================================

async function anomaly(dataset) {

    try {

        const response = await fetch(API_URL + "/anomaly", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                dataset: dataset

            })

        });

        return await response.json();

    }

    catch (error) {

        console.log(error);

    }

}