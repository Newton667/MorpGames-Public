// shared.js
async function updateGreeting() {
    try {
        const response = await fetch('https://morpgames-0vdf.onrender.com/user', {
            credentials: 'include', // Include cookies for session
        });
        if (response.ok) {
            const data = await response.json();
            document.getElementById('user-greeting').textContent = `Hello ${data.username || 'Guest'}!`;
        } else {
            console.error('Failed to fetch user data. Defaulting to guest.');
            document.getElementById('user-greeting').textContent = 'Hello Guest!';
        }
    } catch (err) {
        console.error('Error fetching user data:', err);
        document.getElementById('user-greeting').textContent = 'Hello Guest!';
    }
}

// Call `updateGreeting` after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    updateGreeting();
});

