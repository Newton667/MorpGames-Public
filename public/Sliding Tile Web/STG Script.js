document.addEventListener("DOMContentLoaded", () => 
{
	const menu = document.getElementById("menu");
	const gameContainer = document.getElementById("game-container");
	const tracklistingContainer = document.getElementById("tracklisting");
	const board = document.getElementById("board");
	const startButton = document.getElementById("start-button");
	const showLeaderboardButton = document.getElementById("leaderboard-button");
	const showTracklistingButton = document.getElementById("tracklisting-button");
	const scrambleButton = document.getElementById("scramble-button");
	const submitScoreButton = document.getElementById("submit-score-button");
	const returnButton1 = document.getElementById("return-button-1");
	const returnButton2 = document.getElementById("return-button-2");
	const widthInput = document.getElementById("width-input");
	const heightInput = document.getElementById("height-input");
	const winMessage = document.getElementById("win-message");
	const moveCounter = document.getElementById("move-counter");

	let width, height, size, tiles, blankTile, moveCount, timerInterval, startTime;
	let elapsedTime = 0;
	let disableWinCheck = true;

  // Audio setup
	const backgroundMusic = document.getElementById("background-music");
	const playlist = 
	[
		"STG Audio/sweet dreams but i put kahoot music over it but i fixed the tempo but i reuploaded it ages later.mp3",
		"STG Audio/Kahoot! OST - One-Winged Angel.mp3",
		"STG Audio/James Shimoji - Pepsi Man Theme Song (ORIGINAL).mp3",
		"STG Audio/Roy's Smooth Sounds (SIDE A).mp3",
		"STG Audio/SPEED OF HELL.mp3",
		"STG Audio/Dantes Army.mp3",
		"STG Audio/064 - Temporal Tower - (Pokémon Mystery Dungeon - Explorers of Sky).mp3",
		"STG Audio/Mega Man_ Powered Up - Time Man.mp3",
		"STG Audio/Rolling Down The Street, In My Katamari.mp3",
		"STG Audio/Surfing on a Sine Wave.mp3"
	];

	let currentTrackIndex = 0;

	function playSong(index) 
	{
		if (index >= playlist.length) 
		{
			currentTrackIndex = 0; // Loop back to the first track
		}
		backgroundMusic.src = playlist[currentTrackIndex];
		backgroundMusic.load();
		backgroundMusic.play().catch(error => 
		{
			console.log("Playback error: ", error);
		});
	}

	backgroundMusic.addEventListener("ended", () => 
	{
		currentTrackIndex++;
		playSong(currentTrackIndex);
	});

	backgroundMusic.volume = 0.5;
	playSong(currentTrackIndex);

  // Start Game
	startButton.addEventListener("click", () => 
	{
    // Get dimensions from inputs
		width = Math.max(3, Math.min(20, parseInt(widthInput.value, 10)));
		height = Math.max(3, Math.min(20, parseInt(heightInput.value, 10)));
		size = width * height; // Total number of tiles

    // Hide menu and show game
		menu.style.display = "none";
		gameContainer.style.display = "block";

		initializeBoard();
	});

	widthInput.addEventListener("input", () => 
	{
		if (widthInput.value < 3) widthInput.value = 3;
		if (widthInput.value > 13) widthInput.value = 13;
	});

	heightInput.addEventListener("input", () => 
	{
		if (heightInput.value < 3) heightInput.value = 3;
		if (heightInput.value > 13) heightInput.value = 13;
	});

  // Initialize the board
	function initializeBoard() 
	{
    // Create an array of numbers from 1 to size - 1, then add the blank tile ("")
		tiles = Array.from({ length: size - 1 }, (_, i) => i + 1).concat("");
		blankTile = { row: height - 1, col: width - 1 };
		renderBoard();

    // Scramble and then enable win checking
		disableWinCheck = true;
		scrambleBoard();
		disableWinCheck = false;
		moveCount = 0;

		updateMoveCounter();
		winMessage.textContent = ""; // Clear the win message
		submitScoreButton.style.display = "none";
    
		clearInterval(timerInterval);
		elapsedTime = 0;
		startTime = Date.now();
		timerInterval = setInterval(updateTimer, 1);
	}

	function renderBoard() 
	{
		board.innerHTML = "";
		board.style.gridTemplateColumns = `repeat(${width}, 50px)`;
		board.style.gridAutoRows = `50px`;

		tiles.forEach((value, index) => 
		{
			const tile = document.createElement("div");

			if (value === "") 
			{
				tile.className = "tile blank";
			} 
			else if (value === index + 1) 
			{
				tile.className = "tile correct";
			} 
			else 
			{
				tile.className = "tile incorrect";
			}

			tile.textContent = value;
			tile.dataset.index = index;
			tile.addEventListener("click", () => moveTile(index));
			board.appendChild(tile);
		});
	}

  // Move tile if adjacent to the blank
	function moveTile(index) 
	{
		const row = Math.floor(index / width);
		const col = index % width;
		const isAdjacent =
			(row === blankTile.row && Math.abs(col - blankTile.col) === 1) ||
			(col === blankTile.col && Math.abs(row - blankTile.row) === 1);

		if (isAdjacent) 
		{
			const blankIndex = blankTile.row * width + blankTile.col;
			[tiles[index], tiles[blankIndex]] = [tiles[blankIndex], tiles[index]];
			blankTile = { row, col };

			moveCount++;
			renderBoard();
			updateMoveCounter();
			checkWin();
		}
	}

	document.addEventListener("keydown", (event) => 
	{
		switch (event.key) 
		{
			case "ArrowUp":
				moveTileInDirection("up");
				break;
			case "ArrowDown":
				moveTileInDirection("down");
				break;
			case "ArrowLeft":
				moveTileInDirection("left");
				break;
			case "ArrowRight":
				moveTileInDirection("right");
				break;
		}
	});
	
	function moveTileInDirection(direction) 
	{
		let targetRow = blankTile.row;
		let targetCol = blankTile.col;

		switch (direction) 
		{
			case "up":
				if (blankTile.row > 0) targetRow--;
				break;
			case "down":
				if (blankTile.row < height - 1) targetRow++;
				break;
			case "left":
				if (blankTile.col > 0) targetCol--;
				break;
			case "right":
				if (blankTile.col < width - 1) targetCol++;
				break;
		}

		const targetIndex = targetRow * width + targetCol;
		moveTile(targetIndex);
	}

  // Scramble the board
	function scrambleBoard() 
	{
		for (let i = 0; i < 10000; i++) 
		{
			const direction = Math.floor(Math.random() * 4);
			let targetIndex;

			switch (direction) 
			{
				case 0: 
					targetIndex = blankTile.row > 0 ? (blankTile.row - 1) * width + blankTile.col : null; 
					break; // UP
				case 1: 
					targetIndex = blankTile.row < height - 1 ? (blankTile.row + 1) * width + blankTile.col : null; 
					break; // DOWN
				case 2: 
					targetIndex = blankTile.col > 0 ? blankTile.row * width + blankTile.col - 1 : null; 
					break; // LEFT
				case 3: 
					targetIndex = blankTile.col < width - 1 ? blankTile.row * width + blankTile.col + 1 : null; 
					break; // RIGHT
			}

			if (targetIndex !== null) moveTile(targetIndex);
		}
	}

	function updateTimer() 
	{
		const currentTime = Date.now();
		elapsedTime = currentTime - startTime;

		const minutes = Math.floor(elapsedTime / 60000);
		const seconds = Math.floor((elapsedTime % 60000) / 1000);
		const milliseconds = Math.floor(elapsedTime % 1000);

		document.getElementById("timer").textContent = `Time Elapsed: ${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}.${milliseconds.toString().padStart(3, "0")}`;
	}

  // Update the move counter display
	function updateMoveCounter() 
	{
		moveCounter.textContent = `Moves: ${moveCount}`;
	}

  // Check if the board is in a solved state
	function checkWin() 
	{
		if (!disableWinCheck && tiles.slice(0, -1).every((tile, i) => tile === i + 1)) 
		{
			winMessage.textContent = "Congratulations! You solved the puzzle!";
			submitScoreButton.style.display = "inline-block";
			clearInterval(timerInterval);
		}
	}

	scrambleButton.addEventListener("click", initializeBoard);

	returnButton1.addEventListener("click", () => 
	{
		gameContainer.style.display = "none";
		menu.style.display = "block";
	});
  
	returnButton2.addEventListener("click", () => 
	{
		tracklistingContainer.style.display = "none";
		menu.style.display = "block";
	});

	showLeaderboardButton.addEventListener("click", () => 
	{
		alert("I.O.U. One Leaderboard");
	});
  
	showTracklistingButton.addEventListener("click", () => 
	{
		menu.style.display = "none";
		tracklistingContainer.style.display = "block";
	});

	submitScoreButton.addEventListener("click", () => 
	{
		const playerName = prompt("Enter Name:");
		if (playerName) 
		{
			const minutes = Math.floor(elapsedTime / 60000);
			const seconds = Math.floor((elapsedTime % 60000) / 1000);
			const milliseconds = Math.floor(elapsedTime % 1000);
			alert(`High Score Submitted: ${playerName} - ${moveCount} (${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}.${milliseconds.toString().padStart(3, "0")})`);
		}
	});
});
