const listContentClients = document.querySelector('.listContentClients');

const fetchSettings = {
    limit: 3,
    itterator: [],
    dataPos: 1,
}

let resp = await fetch('/api-dev/users')
fetchSettings.itterator = (await resp.json()).list

for (let i = 0; i < fetchSettings.itterator.length; i++) {
    console.log(fetchSettings.itterator)
    if (i === fetchSettings.limit) {
        break;
    }
    const el = document.createElement("li");
    const svgEl = document.createElement("span");
    el.className = "elContainer";
    el.style.cssText = `
        display: flex; 
        flex-direction: row-reverse;
        justify-content: flex-end;
        padding: 0;
        margin: 30px;
        align-items: center;
    `
    svgEl.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="currentColor" class="bi bi-person-square" viewBox="0 0 16 16">
    <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
    <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2zm12 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1v-1c0-1-1-4-6-4s-6 3-6 4v1a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12z"/>
    </svg>
    `
    svgEl.style.cssText = `
        margin-right: 24px;
    `
    el.textContent = fetchSettings.itterator[i][fetchSettings.dataPos];
    listContentClients.append(el);
    el.appendChild(svgEl);

}
