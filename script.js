// Données statiques
const software = [
    { id: 1, name: "Flash", category: "Troll", description: "Script faisant appraître régulièrement des flashs, mode online. ⚠️ Assets Obligatoire ⚠️", version: "v0", size: "145 MB", downloads: "12.5K", path: "./files/script/online_flash.py", assets: "./files/assets/flash_sound.mp3" },
    { id: 2, name: "VaultSecure", category: "Sécurité", description: "Gestionnaire de mots de passe sécurisé", version: "v1.8.3", size: "32 MB", downloads: "8.2K", path: "./files/script", assets: "./files/assets/" },
    { id: 3, name: "SpeedRunner", category: "Utilitaires", description: "Optimiseur système intelligent", version: "v3.1.0", size: "67 MB", downloads: "15.7K", path: "./files/script", assets: "./files/assets/" },
    { id: 4, name: "Terminal Pro", category: "Développement", description: "Terminal avancé avec IA", version: "v4.0.2", size: "89 MB", downloads: "9.3K", path: "./files/script", assets: "./files/assets/" }
  ];
  
  // Pages
  function showPage(page) {
    document.getElementById('home').classList.toggle('hidden', page !== 'home');
    document.getElementById('library').classList.toggle('hidden', page !== 'library');
  }
  
  // Remplir stats
  document.getElementById('countSoft').textContent = software.length;
  
  // Recherche dynamique
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.toLowerCase();
    let html = '';
  
    if (query) {
      const filtered = software.filter(item =>
        item.name.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query)
      );
  
      filtered.forEach(s => {
        html += `
          <div class="p-4 bg-white/10 mb-2 border border-white/20 hover:bg-white/20 transition">
            <h3 class="font-bold">${s.name}</h3>
            <p class="text-white/60">${s.description}</p>
            <a href="${s.path}" download class="mt-2 px-4 py-2 bg-white text-black text-sm inline-block">Télécharger</a>
            <a href="${s.assets}" download class="mt-2 px-4 py-2 bg-white text-black text-sm inline-block">Assets</a>
          </div>
        `;
      });
    }
    searchResults.innerHTML = html;
  });
  
  // Affichage Bibliothèque
  const libraryList = document.getElementById('libraryList');
  software.forEach(s => {
    libraryList.innerHTML += `
      <div class="p-6 bg-white/5 border border-white/10 hover:border-white/30 transition">
        <h3 class="text-xl font-bold mb-1">${s.name}</h3>
        <p class="text-white/60 mb-2">${s.description}</p>
        <p class="text-white/40 text-sm">${s.category} • ${s.version} • ${s.size} • ${s.downloads} téléchargements</p>
      </div>
    `;
  });
  