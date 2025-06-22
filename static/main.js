// static/main.js

// Auto-refresh home feed every 10 seconds
function refreshFeed() {
    fetch('/api/feed')
        .then(response => response.json())
        .then(data => {
            let feedContainer = document.getElementById('feed-container');
            feedContainer.innerHTML = ''; // clear previous feed
            data.feed.forEach(post => {
                let postDiv = document.createElement('div');
                postDiv.className = 'card mb-2';
                postDiv.innerHTML = `
                    <div class="card-body">
                        <strong>${post.username}</strong>: ${post.content}
                    </div>`;
                feedContainer.appendChild(postDiv);
            });
        })
        .catch(err => console.error('Error fetching feed:', err));
}

// Only auto-refresh on Home page (route '/')
if (window.location.pathname === "/") {
    setInterval(refreshFeed, 10000); // refresh every 10 seconds
}
