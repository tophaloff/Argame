<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameValue - Argus Jeux Vidéo (V2)</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Montserrat:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --main-bg-start: #0f2027; /* Dark Blue */
            --main-bg-end: #203a43; /* Darker Blue */
            --accent-green: #2ecc71; /* Bright Green */
            --light-text: #ecf0f1; /* Light Gray */
            --dark-bg-card: #2c3e50; /* Darker Blue Gray */
            --card-hover: #34495e; /* Even Darker Blue Gray */
            --input-bg: #34495e;
            --button-bg: #00b894; /* Teal */
            --button-hover: #00a082;
            --shadow-color: rgba(0, 0, 0, 0.4);
        }

        body {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, var(--main-bg-start), var(--main-bg-end));
            color: var(--light-text);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            overflow-x: hidden;
        }

        h2 {
            font-family: 'Orbitron', sans-serif;
            color: var(--accent-green);
            font-size: 2.5em;
            margin-bottom: 30px;
            text-shadow: 0 0 15px var(--accent-green);
        }

        .container {
            background: var(--dark-bg-card);
            padding: 30px;
            border-radius: 20px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 8px 30px var(--shadow-color);
            transition: all 0.3s ease-in-out;
        }

        .search-area {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 25px;
        }

        .search-input-group {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        input[type="text"] {
            flex-grow: 1;
            padding: 14px;
            border-radius: 10px;
            border: none;
            background: var(--input-bg);
            color: var(--light-text);
            font-size: 1.1em;
            outline: none;
            box-shadow: inset 0 2px 5px var(--shadow-color);
            transition: all 0.3s ease;
        }

        input[type="text"]::placeholder {
            color: rgba(236, 240, 241, 0.6);
        }

        input[type="text"]:focus {
            box-shadow: 0 0 0 3px var(--accent-green);
        }

        .icon-button {
            background: var(--button-bg);
            border: none;
            border-radius: 10px;
            padding: 12px 15px;
            color: var(--light-text);
            font-size: 1.2em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            transition: background 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 10px var(--shadow-color);
        }

        .icon-button:hover {
            background: var(--button-hover);
            transform: translateY(-2px);
        }

        .icon-button:active {
            transform: translateY(0);
            box-shadow: 0 2px 5px var(--shadow-color);
        }

        .search-button {
            width: 100%;
            background: var(--accent-green);
            color: var(--dark-bg-card);
            font-weight: bold;
            font-size: 1.2em;
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
            border: none;
            transition: background 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 10px var(--shadow-color);
        }

        .search-button:hover {
            background: #27ae60; /* Darker green */
            transform: translateY(-2px);
        }

        .result-card {
            background: var(--card-hover); /* Lighter than main container */
            border-radius: 15px;
            overflow: hidden;
            margin-top: 30px;
            display: none; /* Hidden by default */
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease-out, transform 0.5s ease-out;
            box-shadow: 0 6px 20px var(--shadow-color);
        }

        .result-card.active {
            display: block; /* Show when active */
            opacity: 1;
            transform: translateY(0);
        }

        .game-info {
            padding: 20px;
            text-align: center;
            background: linear-gradient(45deg, #34495e, #4a657c);
            border-bottom: 2px solid var(--accent-green);
        }

        .game-info img {
            max-width: 120px;
            height: auto;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px var(--shadow-color);
        }

        .game-info h3 {
            font-family: 'Orbitron', sans-serif;
            margin: 0 0 5px 0;
            color: var(--light-text);
            font-size: 1.8em;
        }

        .game-info p {
            margin: 0;
            color: #bdc3c7;
            font-size: 0.95em;
        }

        .price-section {
            padding: 20px;
        }

        .price-tag {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 1.1em;
        }

        .price-tag:last-child {
            border-bottom: none;
        }

        .price-value {
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            color: var(--accent-green);
            font-size: 1.3em;
            text-shadow: 0 0 5px rgba(46, 204, 113, 0.5);
        }

        .price-trend {
            font-size: 0.9em;
            margin-left: 10px;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .trend-up { color: #2ecc71; }
        .trend-down { color: #e74c3c; }
        .trend-stable { color: #f1c40f; }

        /* Font Awesome for icons */
        .fa {
            font-size: 1.2em;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>

    <h2>GameValue <span style="font-size:0.7em;">👾</span> Argus</h2>
    
    <div class="container">
        <div class="search-area">
            <div class="search-input-group">
                <input type="text" id="gameInput" placeholder="Rechercher un jeu (ex: Zelda Ocarina of Time)...">
                <button class="icon-button" onclick="simulateBarcodeScan()" title="Simuler scan code-barres">
                    <i class="fas fa-barcode"></i>
                </button>
                <button class="icon-button" onclick="simulateImageRecognition()" title="Simuler reconnaissance image">
                    <i class="fas fa-camera"></i>
                </button>
            </div>
            <button class="search-button" onclick="searchGame()">
                <i class="fas fa-search"></i> RECHERCHER LA COTE
            </button>
        </div>

        <div id="result" class="result-card">
            <div class="game-info">
                <img id="gameImage" src="https://via.placeholder.com/120x160?text=Jeu" alt="Jaquette du jeu">
                <h3 id="resTitle">Nom du jeu</h3>
                <p id="resPlatform">Console</p>
                <p id="resRelease">Date de sortie : --</p>
            </div>
            <div class="price-section">
                <div class="price-tag">
                    <span>Cartouche Seule / Loose</span> 
                    <span class="price-value" id="pLoose">-- €</span>
                    <span class="price-trend trend-up" id="trendLoose"><i class="fas fa-arrow-up"></i> +5%</span>
                </div>
                <div class="price-tag">
                    <span>Complet (CIB)</span> 
                    <span class="price-value" id="pCib">-- €</span>
                    <span class="price-trend trend-stable" id="trendCib"><i class="fas fa-arrow-right"></i> Stable</span>
                </div>
                <div class="price-tag">
                    <span>Neuf Scellé (New)</span> 
                    <span class="price-value" id="pNew">-- €</span>
                    <span class="price-trend trend-down" id="trendNew"><i class="fas fa-arrow-down"></i> -2%</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        function searchGame() {
            const game = document.getElementById('gameInput').value.trim();
            const resultCard = document.getElementById('result');

            if (!game) {
                alert("Veuillez entrer le nom d'un jeu !");
                resultCard.classList.remove('active');
                return;
            }

            // Simulate API call for game data and prices
            setTimeout(() => {
                resultCard.classList.add('active'); // Show card with animation
                document.getElementById('resTitle').innerText = game;
                document.getElementById('resPlatform').innerText = "Nintendo 64 (PAL)";
                document.getElementById('resRelease').innerText = "Date de sortie : 11 Décembre 1998";
                document.getElementById('gameImage').src = 'https://picsum.photos/120/160?' + Math.random(); // Random image

                // Simulate prices and trends
                document.getElementById('pLoose').innerText = "45.00 €";
                document.getElementById('pCib').innerText = "120.00 €";
                document.getElementById('pNew').innerText = "850.00 €";

                // Update trends (random for demo)
                updateTrend('trendLoose', 'up');
                updateTrend('trendCib', 'stable');
                updateTrend('trendNew', 'down');

            }, 500); // Simulate network delay
        }

        function updateTrend(elementId, trendType) {
            const element = document.getElementById(elementId);
            element.className = 'price-trend'; // Reset classes
            let icon = '';
            let text = '';

            switch(trendType) {
                case 'up':
                    element.classList.add('trend-up');
                    icon = '<i class="fas fa-arrow-up"></i>';
                    text = ' +5%'; // Fictive value
                    break;
                case 'down':
                    element.classList.add('trend-down');
                    icon = '<i class="fas fa-arrow-down"></i>';
                    text = ' -2%'; // Fictive value
                    break;
                case 'stable':
                default:
                    element.classList.add('trend-stable');
                    icon = '<i class="fas fa-arrow-right"></i>';
                    text = ' Stable';
                    break;
            }
            element.innerHTML = icon + text;
        }

        function simulateBarcodeScan() {
            alert("Simulation : Ouverture de la caméra pour le scan de code-barres... (fonctionnalité avancée)");
            document.getElementById('gameInput').value = "Super Mario 64 (Scanné)"; // Simulate input
            searchGame();
        }

        function simulateImageRecognition() {
            alert("Simulation : Envoi d'une image pour reconnaissance... (fonctionnalité IA très avancée)");
            document.getElementById('gameInput').value = "Loose Cartridge (Reconnue)"; // Simulate input
            searchGame();
        }
    </script>
</body>
</html>
