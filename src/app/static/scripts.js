// Check if we're on the battle page or the index page
const isBattlePage = window.location.pathname.includes('battle-ui');

// Common utility functions
function getElementId(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with ID ${elementId} not found`);
    }
    return element;
}

// Handle the index page logic
if (!isBattlePage) {
    const battleForm = getElementId('battle-form');
    const exampleElements = document.querySelectorAll('.example');

    // Setup example click handlers
    exampleElements.forEach(example => {
        example.addEventListener('click', () => {
            const rapperA = example.getAttribute('data-rapper-a');
            const rapperB = example.getAttribute('data-rapper-b');

            getElementId('rapperA').value = rapperA;
            getElementId('rapperB').value = rapperB;
        });
    });

    // Handle form submission
    battleForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const rapperA = getElementId('rapperA').value.trim();
        const rapperB = getElementId('rapperB').value.trim();
        const rounds = parseInt(getElementId('rounds').value);

        if (!rapperA || !rapperB) {
            alert('Please enter names for both rappers');
            return;
        }

        try {
            const response = await fetch('/battle/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    rapper_a: rapperA,
                    rapper_b: rapperB,
                    rounds: rounds
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const battleData = await response.json();

            // Redirect to battle page with battle ID
            window.location.href = `/battle-ui?battle_id=${battleData.id || 'new'}`;
        } catch (error) {
            console.error('Error starting battle:', error);
            alert(`Failed to start battle: ${error.message}`);
        }
    });
}
// Handle the battle page logic
else {
    // Get the battle ID from URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const battleId = urlParams.get('battle_id');

    if (!battleId) {
        window.location.href = '/';
    }

    // Get elements
    const rapperAName = getElementId('rapper-a-name');
    const rapperBName = getElementId('rapper-b-name');
    const currentRound = getElementId('current-round');
    const totalRounds = getElementId('total-rounds');
    const battleArena = getElementId('battle-arena');
    const startButton = getElementId('start-button');
    const newBattleButton = getElementId('new-battle-button');
    const loadingIndicator = getElementId('loading-indicator');
    const loadingText = getElementId('loading-text');

    let battle = {
        rapper_a: 'Loading...',
        rapper_b: 'Loading...',
        current_round: 0,
        total_rounds: 5,
        verses: []
    };

    let battleStream = null;
    let battleComplete = false;

    // Fetch initial battle data
    async function fetchBattleData() {
        try {
            const response = await fetch(`/battle/battle/${battleId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            battle = await response.json();

            // Update UI with battle data
            rapperAName.textContent = battle.rapper_a;
            rapperBName.textContent = battle.rapper_b;
            currentRound.textContent = battle.current_round;
            totalRounds.textContent = battle.total_rounds;

            // If there are already verses, display them
            if (battle.verses && battle.verses.length > 0) {
                battle.verses.forEach(verse => {
                    addVerseToUI(verse);
                });
            }

            // If battle is already complete, update UI
            if (battle.complete) {
                battleComplete = true;
                showBattleComplete();
            }
        } catch (error) {
            console.error('Error fetching battle data:', error);
            alert(`Failed to load battle: ${error.message}`);
        }
    }

    // Add a verse to the UI
    function addVerseToUI(verse, animate = false) {
        const verseElement = document.createElement('div');
        verseElement.className = verse.rapper === battle.rapper_a ? 'verse-container verse-left' : 'verse-container verse-right';

        const verseHeader = document.createElement('div');
        verseHeader.className = 'verse-header';
        verseHeader.textContent = verse.rapper;

        const verseContent = document.createElement('div');
        verseContent.className = 'verse-content';
        if (animate) {
            verseContent.classList.add('typing-animation');
        }
        verseContent.textContent = verse.content;

        verseElement.appendChild(verseHeader);
        verseElement.appendChild(verseContent);

        battleArena.appendChild(verseElement);
        battleArena.scrollTop = battleArena.scrollHeight;
    }

    // Start the battle stream
    async function startBattleStream() {
        try {
            // Show loading indicator
            loadingIndicator.style.display = 'block';
            startButton.style.display = 'none';

            // Start the stream
            const response = await fetch(`/battle/battle_stream/${battleId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let currentVerseContent = '';
            let currentRapperName = '';
            let verseAdded = false;

            while (true) {
                const { value, done } = await reader.read();

                if (done) break;

                const text = decoder.decode(value);
                const messages = text.split('\n').filter(line => line.trim());

                for (const message of messages) {
                    try {
                        const parsedResponse = JSON.parse(message);

                        // Update loading text
                        if (parsedResponse.rapper) {
                            loadingText.textContent = `${parsedResponse.rapper} is dropping bars...`;
                            currentRapperName = parsedResponse.rapper;
                        }

                        // Update verse content
                        if (parsedResponse.verse) {
                            currentVerseContent = parsedResponse.verse;
                        }

                        // If complete verse, add to UI
                        if (parsedResponse.complete && !verseAdded) {
                            const newVerse = {
                                content: currentVerseContent,
                                rapper: currentRapperName
                            };

                            addVerseToUI(newVerse, true);

                            // Update round information
                            currentRound.textContent = parsedResponse.round;

                            // Reset for next verse
                            currentVerseContent = '';
                            verseAdded = true;

                            // Small delay before showing loading for next verse
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            verseAdded = false;
                        }

                        // Handle errors
                        if (parsedResponse.error) {
                            console.error('Error from server:', parsedResponse.error);
                            alert(`Error: ${parsedResponse.error}`);
                            break;
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e, message);
                    }
                }
            }

            // Battle is complete
            showBattleComplete();

        } catch (error) {
            console.error('Error in battle stream:', error);
            alert(`Battle error: ${error.message}`);
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    // Show battle complete UI
    function showBattleComplete() {
        battleComplete = true;
        loadingIndicator.style.display = 'none';
        startButton.style.display = 'none';
        newBattleButton.style.display = 'block';

        // Add a battle complete message
        const completeElement = document.createElement('div');
        completeElement.className = 'battle-complete';
        completeElement.innerHTML = '<h3>Battle Complete!</h3><p>Who won? You decide!</p>';
        battleArena.appendChild(completeElement);
    }

    // Event listeners
    startButton.addEventListener('click', () => {
        if (!battleComplete) {
            startBattleStream();
        }
    });

    newBattleButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    // Initialize page
    fetchBattleData();
}