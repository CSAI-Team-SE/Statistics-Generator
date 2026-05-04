const aiQuestionForm = document.getElementById("ai-question-form");
const questionInput = document.getElementById("question");
const aiOutput= document.getElementById("ai-output");
const aiSubmitButton = document.getElementById("ai-submit-btn");

const previousPromptKey = "graphOutputPreviousPrompt";
const previousResponseKey = "graphOutputPreviousResponse";

let previousPrompt = localStorage.getItem(previousPromptKey) || ""; // Initialise previousPrompt from localStorage or set to empty string if not found
let previousResponse = localStorage.getItem(previousResponseKey) || ""; // Initialise previousResponse from localStorage or set to empty string if not found

function getSavedGraphResults() { // This function retrieves the saved graph results from localStorage and parses it as JSON. If there is an error during parsing, it logs the error and returns null.
    const savedGraphResults = localStorage.getItem("graph_result");

    if (!savedGraphResults) {
        return null;
    }

    try{
        return JSON.parse(savedGraphResults);
    } catch (error) {
        console.error("Error parsing saved graph results:", error);
        return null;
    }
}

function getSavedGraphRequest() { // This function retrieves the saved graph request from localStorage and parses it as JSON. If there is an error during parsing, it logs the error and returns null.
    const savedGraphRequest = localStorage.getItem("graph_request");

    if (!savedGraphRequest) {
        return null;
    }

    try{
        return JSON.parse(savedGraphRequest);
    } catch (error) {
        console.error("Error parsing saved graph request:", error);
        return null;
    }
}

function getStatisticsText() { // This function retrieves the text content of the statistics section from the document. If the section is not found, it returns an empty string.
    const statisticsSection = document.getElementById("statistics-section");
    if (statisticsSection == null) {
        return "";
    }

    return statisticsSection.innerText || "";

}


// This function builds a data context string by gathering information from the saved graph results, saved graph request, and the statistics text displayed on the page. 
// It formats this information in a readable way and returns it as a single string. If no data is found, it returns a message indicating that no graph data was found.

function buildDataContext() { 
    const graphResults = getSavedGraphResults();
    const graphRequest = getSavedGraphRequest();
    const statisticsText = getStatisticsText();

    let dataContext = "";

    if (graphRequest !== null) {
        dataContext += "Graph options selected by user:\n";
        dataContext += JSON.stringify(graphRequest, null, 2);
        dataContext += "\n\n";
    }

    if (statisticsText !== "") {
        dataContext += "Statistics displayed on the graph output page:\n";
        dataContext += statisticsText;
        dataContext += "\n\n";
    }

    if (graphResults !== null && graphResults.stats) {
        dataContext += "Raw statistics returned by the graph generation:\n";
        dataContext += JSON.stringify(graphResults.stats, null, 2);
        dataContext += "\n\n";
    }

    if (dataContext === "") {
        dataContext = "No graph data was found in the page or local storage.";
    }

    return dataContext;
}


// This function updates the state of the AI question form's submit button based on whether a loading state is active. 
// If isLoading is true, it disables the button and changes its text to "Loading...". If isLoading is false, it enables the button and resets its text to "Submit".  
 
function setLoadingState(isLoading) {
    if (isLoading) {
        aiSubmitButton.disabled = true;
        aiSubmitButton.innerText = "Generating...";
    } else {
        aiSubmitButton.disabled = false;
        aiSubmitButton.innerText = "Submit";
    }
}

function showMessage(message){ // This function displays a message in the aiOutput element by setting its text content to the provided message string.
    aiOutput.textContent = message;
}

function clearOutput(){ // This function clears the content of the aiOutput element by setting its text content to an empty string.
    aiOutput.textContent = "";
}

function addTextToOutput(text){ // This function appends the provided text to the existing content of the aiOutput element by concatenating the new text to the current text content.
    aiOutput.textContent += text;
}


// This function sends a prompt to the server by making a POST request to the "/api/prompt/stream" endpoint. It includes the prompt text, data context, previous prompt, and previous response in the request body as JSON. 
// The function returns the response from the server. If there is an error during the fetch operation, it will throw an error that can be caught by the caller.

async function sendPrompt(promptText) { 
    const dataContext = buildDataContext();

    const response = await fetch("/api/prompt/stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            prompt: promptText,
            data_context: dataContext,
            previous_prompt: previousPrompt,
            previous_response: previousResponse,
        }),
    });

    return response;
}

// This function reads a streaming response from the server. It uses a ReadableStream reader to read chunks of data as they arrive, decodes them as UTF-8 text, and appends them to the aiOutput element in real-time.
async function readStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let fullResponse = "";

    while (true) {
        const result = await reader.read();

        if (result.done) {
            break;
        }

        const chunk = decoder.decode(result.value, { stream: true });

        fullResponse += chunk;
        addTextToOutput(chunk);
    }
    return fullResponse;

}

    

// This function saves the previous prompt and response to both local variables and localStorage. 
// It takes the prompt text and response text as arguments, updates the previousPrompt and previousResponse variables, and then stores them in localStorage using the defined keys.

function savePreviousInteraction(promptText, responseText) { 
    previousPrompt = promptText;
    previousResponse = responseText;

    localStorage.setItem(previousPromptKey, previousPrompt);
    localStorage.setItem(previousResponseKey, previousResponse);
}


// This event listener is attached to the AI question form's submit event. When the form is submitted, it prevents the default form submission behavior, retrieves the prompt text from the input field, and checks if it is empty. 
// If the prompt is valid, it clears the output area, sets the loading state, and sends the prompt to the server using the sendPrompt function. It then reads the streaming response using readStream and saves the previous interaction. 
// If there are any errors during this process, it logs the error and displays an error message to the user. Finally, it resets the loading state once the operation is complete.

aiQuestionForm.addEventListener("submit", async function(event) { 
    event.preventDefault();

    const promptText = questionInput.value.trim();

    if (promptText === "") {
        showMessage("Please enter a question before submitting.");
        return;
    }

    clearOutput();
    setLoadingState(true);

    try {
        const response = await sendPrompt(promptText);
        if (!response.ok) {
            showMessage("There was an error generating the response. Please try again.");
            return;
        }

        const fullResponse = await readStream(response);
        savePreviousInteraction(promptText, fullResponse);

        questionInput.value = "";
    } catch (error) {
        console.error("Error during AI question submission:", error);
        showMessage("An error occurred while submitting your question. Please try again.");
    } finally {
        setLoadingState(false);
    }
});


